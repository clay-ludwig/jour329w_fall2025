#!/usr/bin/env python3
"""
Web-based monitor for the Beat Book Agent

This provides a real-time web interface to watch the agent work.
"""

import json
import anthropic
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from dotenv import load_dotenv
import glob

# Load environment variables from .env file
load_dotenv()

# Import the agent components
from beat_book_agent import StoryDatabase, get_next_version_number

app = Flask(__name__)
app.config['SECRET_KEY'] = 'beat-book-agent-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
agent_state = {
    "status": "idle",
    "iteration": 0,
    "tool_calls": [],
    "messages": [],
    "final_output": None,
    "error": None
}


class WebBeatBookAgent:
    """Beat Book Agent with WebSocket updates"""
    
    def __init__(self, api_key: str, json_path: str, prompt_path: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db = StoryDatabase(json_path)
        
        # Load the prompt
        with open(prompt_path, 'r') as f:
            self.system_prompt = f.read()
        
        self.system_prompt += """

IMPORTANT INSTRUCTIONS FOR USING TOOLS:

You have access to several tools that let you search and explore the story database without loading everything at once. Use these tools strategically to:

1. First, get an overview of the dataset with get_stats()
2. Then search for relevant stories using keywords, topics, tags, or locations
3. When you find interesting stories, get their full details with get_story_details()
4. Look for related stories to understand coverage patterns
5. Filter by high follow-up ratings to find stories with good future angles

Take your time to explore the data thoroughly before writing the beat book. Use multiple tool calls to understand the landscape. Once you have gathered sufficient information, write the complete beat book in a single response.

Remember: You can call tools multiple times to refine your understanding. Don't rush to write - explore first!
"""
        
        self.conversation_history = []
        self.tool_use_log = []
        
    def emit_update(self, event: str, data: Dict):
        """Emit an update to all connected clients"""
        socketio.emit(event, data)
        socketio.sleep(0.1)  # Give time for the message to send
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def _log_tool_call(self, tool_name: str, inputs: Dict[str, Any], result: Any):
        """Log tool usage and emit to web clients"""
        log_entry = {
            "timestamp": self._timestamp(),
            "tool": tool_name,
            "inputs": inputs,
            "result_size": len(str(result)),
            "result_preview": str(result)[:200] if not isinstance(result, list) else f"{len(result)} items"
        }
        self.tool_use_log.append(log_entry)
        
        # Update global state
        agent_state["tool_calls"].append(log_entry)
        
        # Emit to web
        self.emit_update('tool_call', log_entry)
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool call and return the result"""
        
        if tool_name == "get_stats":
            result = self.db.get_stats()
        elif tool_name == "search_by_keyword":
            result = self.db.search_by_keyword(
                keyword=tool_input['keyword'],
                fields=tool_input.get('fields'),
                limit=tool_input.get('limit', 50)
            )
        elif tool_name == "filter_by_topic":
            result = self.db.filter_by_topic(
                topic=tool_input['topic'],
                limit=tool_input.get('limit', 100)
            )
        elif tool_name == "filter_by_tag":
            result = self.db.filter_by_tag(
                tag=tool_input['tag'],
                limit=tool_input.get('limit', 50)
            )
        elif tool_name == "filter_by_location":
            result = self.db.filter_by_location(
                location=tool_input['location'],
                limit=tool_input.get('limit', 50)
            )
        elif tool_name == "get_story_details":
            result = self.db.get_story_details(link=tool_input['link'])
        elif tool_name == "filter_by_category":
            result = self.db.filter_by_category(
                category=tool_input['category'],
                limit=tool_input.get('limit', 100)
            )
        elif tool_name == "filter_by_follow_up_rating":
            result = self.db.filter_by_follow_up_rating(
                min_rating=tool_input['min_rating'],
                limit=tool_input.get('limit', 50)
            )
        elif tool_name == "get_related_stories":
            result = self.db.get_related_stories(
                link=tool_input['link'],
                limit=tool_input.get('limit', 10)
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self._log_tool_call(tool_name, tool_input, result)
        return result
    
    def run(self, model: str = "claude-sonnet-4-5", max_tokens: int = 64000):
        """Run the agent to generate a beat book"""
        
        agent_state["status"] = "running"
        agent_state["iteration"] = 0
        agent_state["tool_calls"] = []
        agent_state["messages"] = []
        agent_state["final_output"] = None
        agent_state["error"] = None
        
        self.emit_update('status_update', {
            "status": "running",
            "message": "Starting beat book generation..."
        })
        
        # Define the tools
        tools = [
            {
                "name": "get_stats",
                "description": "Get overall statistics about the story database, including total stories, topics, categories, and most common tags. Call this first to understand what's available.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "search_by_keyword",
                "description": "Search for stories containing a specific keyword in their title, summary, or tags. Returns simplified story information (without full content).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "The search term to look for"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: Fields to search in (default: title, summary, tags)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 50)"
                        }
                    },
                    "required": ["keyword"]
                }
            },
            {
                "name": "filter_by_topic",
                "description": "Get all stories for a specific topic (e.g., 'Education', 'Health', etc.). Returns simplified story information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to filter by"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 100)"
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "filter_by_tag",
                "description": "Find stories that contain a specific tag. Returns simplified story information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tag": {
                            "type": "string",
                            "description": "The tag to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 50)"
                        }
                    },
                    "required": ["tag"]
                }
            },
            {
                "name": "filter_by_location",
                "description": "Find stories focused on a specific geographic location. Returns simplified story information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 50)"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_story_details",
                "description": "Get the COMPLETE details of a specific story including full content. Use this when you need to read the full story text.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "link": {
                            "type": "string",
                            "description": "The URL/link of the story"
                        }
                    },
                    "required": ["link"]
                }
            },
            {
                "name": "filter_by_category",
                "description": "Filter stories by category type (e.g., 'feature', 'news', 'investigative'). Returns simplified story information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "The story category"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 100)"
                        }
                    },
                    "required": ["category"]
                }
            },
            {
                "name": "filter_by_follow_up_rating",
                "description": "Find stories with a follow-up rating at or above a threshold. Higher ratings indicate better potential for follow-up stories. Returns simplified story information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "min_rating": {
                            "type": "integer",
                            "description": "Minimum follow-up rating (typically 1-10)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 50)"
                        }
                    },
                    "required": ["min_rating"]
                }
            },
            {
                "name": "get_related_stories",
                "description": "Find stories related to a given story based on shared tags and topic. Useful for understanding coverage patterns. Returns simplified story information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "link": {
                            "type": "string",
                            "description": "The URL/link of the story to find related stories for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "required": ["link"]
                }
            }
        ]
        
        # Initialize conversation
        messages = [
            {
                "role": "user",
                "content": "Please generate a comprehensive beat book for the Education topic. Use the available tools to explore the story database and gather relevant information before writing the beat book."
            }
        ]
        
        # Run the agentic loop
        iteration = 0
        max_iterations = 30
        
        try:
            while iteration < max_iterations:
                iteration += 1
                agent_state["iteration"] = iteration
                
                self.emit_update('iteration_update', {
                    "iteration": iteration,
                    "max_iterations": max_iterations
                })
                
                # Make API call with streaming support for long operations
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=self.system_prompt,
                    tools=tools,
                    messages=messages,
                    timeout=600.0  # 10 minute timeout for long operations
                )
                
                self.emit_update('response_received', {
                    "stop_reason": response.stop_reason,
                    "content_blocks": len(response.content)
                })
                
                # Process response
                if response.stop_reason == "end_turn":
                    # Model has finished
                    final_text = ""
                    for block in response.content:
                        if block.type == "text":
                            final_text += block.text
                    
                    agent_state["status"] = "completed"
                    agent_state["final_output"] = final_text
                    
                    self.emit_update('generation_complete', {
                        "output": final_text,
                        "tool_calls": len(self.tool_use_log)
                    })
                    
                    return final_text, self.tool_use_log
                
                elif response.stop_reason == "tool_use":
                    # Model wants to use tools
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Execute all tool calls
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            result = self._execute_tool(block.name, block.input)
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result)
                            })
                    
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                
                else:
                    raise Exception(f"Unexpected stop reason: {response.stop_reason}")
            
            raise Exception("Reached maximum iterations")
            
        except Exception as e:
            agent_state["status"] = "error"
            agent_state["error"] = str(e)
            self.emit_update('error', {"message": str(e)})
            raise


# Flask routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/state')
def get_state():
    """Get current agent state"""
    return jsonify(agent_state)


@socketio.on('start_generation')
def handle_start_generation():
    """Start the beat book generation"""
    
    if agent_state["status"] == "running":
        emit('error', {"message": "Agent is already running"})
        return
    
    # Get API key from environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        emit('error', {"message": "ANTHROPIC_API_KEY not set"})
        return
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(os.path.dirname(script_dir), "enhanced_beat_stories.json")
    prompt_path = os.path.join(os.path.dirname(script_dir), "prompt.txt")
    
    # Run agent in background thread
    def run_agent():
        try:
            agent = WebBeatBookAgent(api_key, json_path, prompt_path)
            beat_book, tool_log = agent.run()
            
            # Save output with version number
            version_num = get_next_version_number(script_dir)
            output_file = os.path.join(script_dir, f"beat_book_v{version_num}.md")
            
            with open(output_file, 'w') as f:
                f.write(beat_book)
            
            log_file = os.path.join(script_dir, f"tool_log_v{version_num}.json")
            with open(log_file, 'w') as f:
                json.dump(tool_log, f, indent=2)
            
        except Exception as e:
            print(f"Error in agent: {e}")
            import traceback
            traceback.print_exc()
    
    thread = threading.Thread(target=run_agent)
    thread.daemon = True
    thread.start()
    
    emit('generation_started', {"message": "Beat book generation started"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*80}")
    print(f"Beat Book Agent Web Monitor")
    print(f"{'='*80}")
    print(f"Open your browser to: http://localhost:{port}")
    print(f"{'='*80}\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
