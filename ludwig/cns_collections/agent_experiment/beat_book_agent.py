#!/usr/bin/env python3
"""
Beat Book Agent with Tool-based JSON Access

This script allows an LLM to generate a beat book by providing it with tool calls
to search and filter through story data without loading everything at once.
"""

import json
import anthropic
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
from collections import Counter
from dotenv import load_dotenv
import glob

# Load environment variables from .env file
load_dotenv()


def get_next_version_number(directory: str) -> int:
    """Find the next version number for beat_book_v{n}.md files"""
    pattern = os.path.join(directory, "beat_book_v*.md")
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    # Extract version numbers from filenames
    versions = []
    for filepath in existing_files:
        filename = os.path.basename(filepath)
        # Extract number from beat_book_v{number}.md
        if filename.startswith("beat_book_v") and filename.endswith(".md"):
            try:
                version_str = filename[len("beat_book_v"):-len(".md")]
                versions.append(int(version_str))
            except ValueError:
                continue
    
    return max(versions) + 1 if versions else 1


class StoryDatabase:
    """Manages the story JSON data and provides search/filter capabilities"""
    
    def __init__(self, json_path: str):
        """Load the JSON data once at initialization"""
        print(f"[{self._timestamp()}] Loading story database from {json_path}...")
        with open(json_path, 'r') as f:
            self.stories = json.load(f)
        print(f"[{self._timestamp()}] ✓ Loaded {len(self.stories)} stories")
        
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics about the dataset"""
        topics = [s.get('topic', 'Unknown') for s in self.stories]
        categories = [s.get('metadata_story_category', 'Unknown') for s in self.stories]
        
        # Get all unique tags
        all_tags = []
        for story in self.stories:
            tags = story.get('tags', [])
            if isinstance(tags, list):
                all_tags.extend(tags)
        
        return {
            "total_stories": len(self.stories),
            "topics": dict(Counter(topics)),
            "categories": dict(Counter(categories)),
            "total_unique_tags": len(set(all_tags)),
            "most_common_tags": dict(Counter(all_tags).most_common(20)),
            "date_range": "Stories from CNS Maryland"
        }
    
    def search_by_keyword(self, keyword: str, fields: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search stories by keyword in specified fields
        
        Args:
            keyword: The search term (case-insensitive)
            fields: List of fields to search in (default: ['title', 'summary', 'tags'])
            limit: Maximum number of results to return
        """
        if fields is None:
            fields = ['title', 'summary', 'tags']
        
        keyword_lower = keyword.lower()
        results = []
        
        for story in self.stories:
            for field in fields:
                value = story.get(field, '')
                if isinstance(value, str):
                    if keyword_lower in value.lower():
                        results.append(self._simplify_story(story))
                        break
                elif isinstance(value, list):
                    if any(keyword_lower in str(item).lower() for item in value):
                        results.append(self._simplify_story(story))
                        break
            
            if len(results) >= limit:
                break
        
        return results
    
    def filter_by_topic(self, topic: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Filter stories by topic"""
        results = [
            self._simplify_story(s) 
            for s in self.stories 
            if s.get('topic', '').lower() == topic.lower()
        ][:limit]
        
        return results
    
    def filter_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Filter stories that contain a specific tag"""
        results = []
        
        for story in self.stories:
            tags = story.get('tags', [])
            if isinstance(tags, list):
                if any(tag.lower() in str(t).lower() for t in tags):
                    results.append(self._simplify_story(story))
                    if len(results) >= limit:
                        break
        
        return results
    
    def filter_by_location(self, location: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Filter stories by geographic focus"""
        location_lower = location.lower()
        results = [
            self._simplify_story(s) 
            for s in self.stories 
            if location_lower in s.get('metadata_geographic_focus', '').lower()
        ][:limit]
        
        return results
    
    def get_story_details(self, link: str) -> Optional[Dict[str, Any]]:
        """Get full details of a specific story by its link"""
        for story in self.stories:
            if story.get('link') == link:
                return story
        return None
    
    def filter_by_category(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Filter stories by story category (e.g., 'feature', 'news', 'investigative')"""
        category_lower = category.lower()
        results = [
            self._simplify_story(s) 
            for s in self.stories 
            if s.get('metadata_story_category', '').lower() == category_lower
        ][:limit]
        
        return results
    
    def filter_by_follow_up_rating(self, min_rating: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Filter stories with follow-up rating >= min_rating"""
        results = [
            self._simplify_story(s) 
            for s in self.stories 
            if s.get('metadata_follow_up_rating', 0) >= min_rating
        ][:limit]
        
        return results
    
    def get_related_stories(self, link: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find stories related to a given story (by shared tags or topic)"""
        story = self.get_story_details(link)
        if not story:
            return []
        
        story_tags = set(story.get('tags', []))
        story_topic = story.get('topic', '')
        
        results = []
        for s in self.stories:
            if s.get('link') == link:
                continue
            
            # Calculate relevance score
            s_tags = set(s.get('tags', []))
            shared_tags = len(story_tags & s_tags)
            same_topic = 1 if s.get('topic') == story_topic else 0
            
            if shared_tags > 0 or same_topic:
                score = shared_tags * 2 + same_topic
                results.append((score, self._simplify_story(s)))
        
        # Sort by relevance and return top results
        results.sort(reverse=True, key=lambda x: x[0])
        return [r[1] for r in results[:limit]]
    
    def _simplify_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """Return a simplified version of a story (without full content)"""
        return {
            "link": story.get('link'),
            "title": story.get('title'),
            "topic": story.get('topic'),
            "tags": story.get('tags', []),
            "summary": story.get('summary'),
            "metadata_geographic_focus": story.get('metadata_geographic_focus'),
            "metadata_story_category": story.get('metadata_story_category'),
            "metadata_follow_up_rating": story.get('metadata_follow_up_rating'),
        }
    
    # ===== NEW CONSOLIDATED & ANALYTICAL TOOLS =====
    
    def get_dataset_overview(self) -> Dict[str, Any]:
        """Get comprehensive overview of the entire dataset with key metrics"""
        topics = [s.get('topic', 'Unknown') for s in self.stories]
        categories = [s.get('metadata_story_category', 'Unknown') for s in self.stories]
        locations = [s.get('metadata_geographic_focus', 'Unknown') for s in self.stories if s.get('metadata_geographic_focus')]
        
        # Get all tags
        all_tags = []
        for story in self.stories:
            tags = story.get('tags', [])
            if isinstance(tags, list):
                all_tags.extend(tags)
        
        # Calculate follow-up potential
        ratings = [s.get('metadata_follow_up_rating', 0) for s in self.stories if s.get('metadata_follow_up_rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        high_potential_count = len([r for r in ratings if r >= 7])
        
        return {
            "total_stories": len(self.stories),
            "topics_breakdown": dict(Counter(topics).most_common()),
            "story_categories": dict(Counter(categories).most_common()),
            "top_locations": dict(Counter(locations).most_common(15)),
            "most_common_tags": dict(Counter(all_tags).most_common(30)),
            "total_unique_tags": len(set(all_tags)),
            "follow_up_metrics": {
                "average_rating": round(avg_rating, 2),
                "high_potential_stories": high_potential_count,
                "stories_with_ratings": len(ratings)
            }
        }
    
    def query_stories(self, topic: Optional[str] = None, keyword: Optional[str] = None, 
                     location: Optional[str] = None, min_follow_up_rating: Optional[int] = None,
                     category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Unified query tool - filter stories by multiple criteria at once
        Returns simplified stories matching ALL specified filters
        """
        results = self.stories.copy()
        
        # Apply filters
        if topic:
            results = [s for s in results if s.get('topic', '').lower() == topic.lower()]
        
        if keyword:
            kw_lower = keyword.lower()
            results = [s for s in results if (
                kw_lower in s.get('title', '').lower() or
                kw_lower in s.get('summary', '').lower() or
                any(kw_lower in str(tag).lower() for tag in s.get('tags', []))
            )]
        
        if location:
            loc_lower = location.lower()
            results = [s for s in results if loc_lower in s.get('metadata_geographic_focus', '').lower()]
        
        if min_follow_up_rating is not None:
            results = [s for s in results if s.get('metadata_follow_up_rating', 0) >= min_follow_up_rating]
        
        if category:
            cat_lower = category.lower()
            results = [s for s in results if s.get('metadata_story_category', '').lower() == cat_lower]
        
        return [self._simplify_story(s) for s in results[:limit]]
    
    def analyze_coverage_patterns(self, topic: str) -> Dict[str, Any]:
        """Analyze coverage patterns for a specific topic to identify themes and trends"""
        topic_stories = [s for s in self.stories if s.get('topic', '').lower() == topic.lower()]
        
        if not topic_stories:
            return {"error": f"No stories found for topic: {topic}"}
        
        # Extract themes from tags
        all_tags = []
        for story in topic_stories:
            tags = story.get('tags', [])
            if isinstance(tags, list):
                all_tags.extend(tags)
        
        # Geographic distribution
        locations = [s.get('metadata_geographic_focus', 'Unknown') for s in topic_stories if s.get('metadata_geographic_focus')]
        
        # Story types
        categories = [s.get('metadata_story_category', 'Unknown') for s in topic_stories]
        
        # Follow-up potential
        high_potential = [self._simplify_story(s) for s in topic_stories if s.get('metadata_follow_up_rating', 0) >= 7]
        
        return {
            "topic": topic,
            "total_stories": len(topic_stories),
            "dominant_themes": dict(Counter(all_tags).most_common(20)),
            "geographic_coverage": dict(Counter(locations).most_common(10)),
            "story_types": dict(Counter(categories)),
            "high_potential_stories_count": len(high_potential),
            "sample_high_potential_stories": high_potential[:5]
        }
    
    def find_coverage_gaps(self, topic: str) -> Dict[str, Any]:
        """Identify potential coverage gaps by analyzing what's been covered vs what might be missing"""
        topic_stories = [s for s in self.stories if s.get('topic', '').lower() == topic.lower()]
        
        if not topic_stories:
            return {"error": f"No stories found for topic: {topic}"}
        
        # Analyze locations covered
        locations = [s.get('metadata_geographic_focus') for s in topic_stories if s.get('metadata_geographic_focus')]
        location_counts = Counter(locations)
        
        # Analyze institutions mentioned
        institutions = []
        for story in topic_stories:
            inst = story.get('metadata_key_institutions', '[]')
            try:
                inst_list = json.loads(inst) if isinstance(inst, str) else inst
                if isinstance(inst_list, list):
                    institutions.extend(inst_list)
            except:
                pass
        
        # Analyze story categories
        categories = [s.get('metadata_story_category') for s in topic_stories if s.get('metadata_story_category')]
        category_counts = Counter(categories)
        
        # Find single-story locations (underreported areas)
        underreported_locations = [loc for loc, count in location_counts.items() if count <= 2]
        
        # Find low-rated stories that might need follow-up
        needs_followup = [
            self._simplify_story(s) for s in topic_stories 
            if s.get('metadata_follow_up_rating', 0) >= 6
        ]
        
        return {
            "topic": topic,
            "total_stories_analyzed": len(topic_stories),
            "locations_covered": len(set(locations)),
            "underreported_locations": underreported_locations[:10],
            "story_type_distribution": dict(category_counts),
            "key_institutions_mentioned": dict(Counter(institutions).most_common(15)),
            "stories_needing_followup": needs_followup[:10],
            "suggestions": {
                "geographic": f"Consider covering: {', '.join(underreported_locations[:5])}" if underreported_locations else "Coverage seems geographically diverse",
                "story_types": f"Underrepresented types: {[t for t,c in category_counts.items() if c < 3]}" if category_counts else "N/A"
            }
        }
    
    def get_institutional_analysis(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Analyze which institutions/organizations appear most frequently in coverage"""
        stories_to_analyze = self.stories
        if topic:
            stories_to_analyze = [s for s in self.stories if s.get('topic', '').lower() == topic.lower()]
        
        institutions = []
        stories_by_institution = {}
        
        for story in stories_to_analyze:
            inst = story.get('metadata_key_institutions', '[]')
            try:
                inst_list = json.loads(inst) if isinstance(inst, str) else (inst if isinstance(inst, list) else [])
                for institution in inst_list:
                    institutions.append(institution)
                    if institution not in stories_by_institution:
                        stories_by_institution[institution] = []
                    stories_by_institution[institution].append(self._simplify_story(story))
            except:
                pass
        
        # Get top institutions with sample stories
        institution_analysis = {}
        for inst, count in Counter(institutions).most_common(15):
            institution_analysis[inst] = {
                "mention_count": count,
                "sample_stories": stories_by_institution[inst][:3]
            }
        
        return {
            "scope": topic if topic else "All topics",
            "total_institutions_mentioned": len(set(institutions)),
            "top_institutions": institution_analysis
        }
    
    def get_geographic_distribution(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Analyze geographic distribution of coverage"""
        stories_to_analyze = self.stories
        if topic:
            stories_to_analyze = [s for s in self.stories if s.get('topic', '').lower() == topic.lower()]
        
        locations = []
        stories_by_location = {}
        
        for story in stories_to_analyze:
            loc = story.get('metadata_geographic_focus')
            if loc:
                locations.append(loc)
                if loc not in stories_by_location:
                    stories_by_location[loc] = []
                stories_by_location[loc].append(self._simplify_story(story))
        
        # Build location analysis
        location_analysis = {}
        for loc, count in Counter(locations).most_common(20):
            location_analysis[loc] = {
                "story_count": count,
                "sample_stories": stories_by_location[loc][:3]
            }
        
        return {
            "scope": topic if topic else "All topics",
            "total_locations_covered": len(set(locations)),
            "location_breakdown": location_analysis,
            "coverage_summary": {
                "heavily_covered": [loc for loc, count in Counter(locations).items() if count >= 5],
                "lightly_covered": [loc for loc, count in Counter(locations).items() if count <= 2]
            }
        }
    
    def analyze_story_themes(self, topic: str, limit: int = 15) -> Dict[str, Any]:
        """Deep analysis of thematic patterns in stories for a topic"""
        topic_stories = [s for s in self.stories if s.get('topic', '').lower() == topic.lower()]
        
        if not topic_stories:
            return {"error": f"No stories found for topic: {topic}"}
        
        # Collect all tags
        all_tags = []
        tag_to_stories = {}
        
        for story in topic_stories:
            tags = story.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    all_tags.append(tag)
                    if tag not in tag_to_stories:
                        tag_to_stories[tag] = []
                    tag_to_stories[tag].append(self._simplify_story(story))
        
        # Build theme analysis
        theme_analysis = {}
        for tag, count in Counter(all_tags).most_common(limit):
            theme_analysis[tag] = {
                "frequency": count,
                "sample_stories": tag_to_stories[tag][:3]
            }
        
        return {
            "topic": topic,
            "total_themes_identified": len(set(all_tags)),
            "recurring_themes": theme_analysis,
            "theme_insights": f"Top themes include: {', '.join([t for t, _ in Counter(all_tags).most_common(5)])}"
        }



class BeatBookAgent:
    """Manages the LLM interaction with tool calling"""
    
    def __init__(self, api_key: str, json_path: str, prompt_path: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db = StoryDatabase(json_path)
        
        # Load the prompt
        with open(prompt_path, 'r') as f:
            self.system_prompt = f.read()
        
        # The prompt.txt file now contains the tool usage strategy
        self.conversation_history = []
        self.tool_use_log = []
        
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def _log_tool_call(self, tool_name: str, inputs: Dict[str, Any], result: Any):
        """Log tool usage for debugging"""
        log_entry = {
            "timestamp": self._timestamp(),
            "tool": tool_name,
            "inputs": inputs,
            "result_size": len(str(result))
        }
        self.tool_use_log.append(log_entry)
        
        print(f"\n[{log_entry['timestamp']}] 🔧 TOOL CALL: {tool_name}")
        print(f"   Inputs: {json.dumps(inputs, indent=2)}")
        
        if isinstance(result, list):
            print(f"   → Returned {len(result)} results")
        elif isinstance(result, dict):
            print(f"   → Returned dict with {len(result)} keys")
        else:
            print(f"   → Returned: {type(result).__name__}")
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool call and return the result"""
        
        # New consolidated tools
        if tool_name == "get_dataset_overview":
            result = self.db.get_dataset_overview()
        elif tool_name == "query_stories":
            result = self.db.query_stories(
                topic=tool_input.get('topic'),
                keyword=tool_input.get('keyword'),
                location=tool_input.get('location'),
                min_follow_up_rating=tool_input.get('min_follow_up_rating'),
                category=tool_input.get('category'),
                limit=tool_input.get('limit', 50)
            )
        elif tool_name == "get_story_details":
            result = self.db.get_story_details(link=tool_input['link'])
        elif tool_name == "analyze_coverage_patterns":
            result = self.db.analyze_coverage_patterns(topic=tool_input['topic'])
        elif tool_name == "find_coverage_gaps":
            result = self.db.find_coverage_gaps(topic=tool_input['topic'])
        elif tool_name == "get_institutional_analysis":
            result = self.db.get_institutional_analysis(topic=tool_input.get('topic'))
        elif tool_name == "get_geographic_distribution":
            result = self.db.get_geographic_distribution(topic=tool_input.get('topic'))
        elif tool_name == "analyze_story_themes":
            result = self.db.analyze_story_themes(
                topic=tool_input['topic'],
                limit=tool_input.get('limit', 15)
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self._log_tool_call(tool_name, tool_input, result)
        return result
    
    def run(self, model: str = "claude-sonnet-4-5", max_tokens: int = 64000):
        """Run the agent to generate a beat book"""
        
        print(f"\n{'='*80}")
        print(f"Starting Beat Book Generation Agent")
        print(f"Model: {model}")
        print(f"{'='*80}\n")
        
        # Define the tools available to the model
        tools = [
            {
                "name": "get_dataset_overview",
                "description": "Get comprehensive overview of the entire dataset including topic breakdown, categories, locations, tags, and follow-up metrics. USE THIS FIRST to understand what data is available.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "query_stories",
                "description": "UNIFIED QUERY TOOL - Filter stories by multiple criteria at once (topic, keyword, location, category, follow-up rating). Returns simplified story summaries. Use this instead of multiple separate filters.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Filter by topic (e.g., 'Education', 'Health')"
                        },
                        "keyword": {
                            "type": "string",
                            "description": "Search keyword in title, summary, or tags"
                        },
                        "location": {
                            "type": "string",
                            "description": "Filter by geographic focus (e.g., 'Baltimore', 'Anne Arundel')"
                        },
                        "min_follow_up_rating": {
                            "type": "integer",
                            "description": "Minimum follow-up rating (1-10, use 7+ for high potential)"
                        },
                        "category": {
                            "type": "string",
                            "description": "Story category (e.g., 'feature', 'news', 'investigative')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 50)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_story_details",
                "description": "Get FULL content of a specific story including complete text. Use sparingly - only for stories you want to cite or analyze deeply.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "link": {
                            "type": "string",
                            "description": "The story URL/link"
                        }
                    },
                    "required": ["link"]
                }
            },
            {
                "name": "analyze_coverage_patterns",
                "description": "Analyze coverage patterns for a specific topic: dominant themes (tags), geographic distribution, story types, and high-potential stories. USE THIS to understand what's been covered.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to analyze (e.g., 'Education')"
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "find_coverage_gaps",
                "description": "Identify coverage gaps and underreported areas for a topic. Shows underreported locations, story type distribution, and stories needing follow-up. USE THIS to find story ideas.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to analyze for gaps"
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "get_institutional_analysis",
                "description": "Analyze which organizations/institutions appear most frequently in coverage. Shows top institutions with sample stories. Helps identify key players on the beat.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Optional: Filter to specific topic"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_geographic_distribution",
                "description": "Analyze geographic coverage patterns. Shows which locations are heavily vs lightly covered. Helps identify geographic angles and gaps.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Optional: Filter to specific topic"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "analyze_story_themes",
                "description": "Deep thematic analysis for a topic. Shows recurring themes (tags) with frequency and sample stories. USE THIS to understand thematic patterns.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to analyze"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top themes to return (default: 15)"
                        }
                    },
                    "required": ["topic"]
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
        
        print(f"[{self._timestamp()}] 🤖 Sending initial request to Claude...\n")
        
        # Run the agentic loop
        iteration = 0
        max_iterations = 30  # Prevent infinite loops
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'─'*80}")
            print(f"[{self._timestamp()}] Iteration {iteration}/{max_iterations}")
            print(f"{'─'*80}")
            
            # Make API call with streaming support for long operations
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=self.system_prompt,
                tools=tools,
                messages=messages,
                timeout=600.0  # 10 minute timeout for long operations
            )
            
            print(f"\n[{self._timestamp()}] 📩 Response received:")
            print(f"   Stop reason: {response.stop_reason}")
            print(f"   Content blocks: {len(response.content)}")
            
            # Process response
            if response.stop_reason == "end_turn":
                # Model has finished - extract the final text
                print(f"\n[{self._timestamp()}] ✅ Model has completed generation!")
                
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text
                
                return final_text, self.tool_use_log
            
            elif response.stop_reason == "tool_use":
                # Model wants to use tools
                print(f"\n[{self._timestamp()}] 🔧 Model is requesting tool calls...")
                
                # Add assistant's response to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Execute all tool calls
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"\n   Tool: {block.name}")
                        
                        # Execute the tool
                        result = self._execute_tool(block.name, block.input)
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result)
                        })
                
                # Add tool results to messages
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
            else:
                print(f"\n[{self._timestamp()}] ⚠️ Unexpected stop reason: {response.stop_reason}")
                break
        
        print(f"\n[{self._timestamp()}] ⚠️ Reached maximum iterations!")
        return None, self.tool_use_log


def main():
    """Main entry point"""
    
    # Configuration
    API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    if not API_KEY:
        print("ERROR: Please set ANTHROPIC_API_KEY environment variable")
        print("Example: export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(os.path.dirname(script_dir), "enhanced_beat_stories.json")
    prompt_path = os.path.join(os.path.dirname(script_dir), "prompt.txt")
    
    # Verify files exist
    if not os.path.exists(json_path):
        print(f"ERROR: Story data not found at {json_path}")
        sys.exit(1)
    
    if not os.path.exists(prompt_path):
        print(f"ERROR: Prompt not found at {prompt_path}")
        sys.exit(1)
    
    # Create agent
    agent = BeatBookAgent(API_KEY, json_path, prompt_path)
    
    # Run agent
    try:
        beat_book, tool_log = agent.run(
            model="claude-sonnet-4-5",
            max_tokens=64000
        )
        
        if beat_book:
            # Find next version number
            version_num = get_next_version_number(script_dir)
            output_file = os.path.join(script_dir, f"beat_book_v{version_num}.md")
            
            with open(output_file, 'w') as f:
                f.write(beat_book)
            
            print(f"\n{'='*80}")
            print(f"✅ Beat book generated successfully!")
            print(f"📄 Output saved to: {output_file}")
            print(f"📝 Version: v{version_num}")
            print(f"🔧 Tool calls made: {len(tool_log)}")
            print(f"{'='*80}\n")
            
            # Save tool log with same version number
            log_file = os.path.join(script_dir, f"tool_log_v{version_num}.json")
            with open(log_file, 'w') as f:
                json.dump(tool_log, f, indent=2)
            
            print(f"📊 Tool usage log saved to: {log_file}\n")
            
            # Print preview
            print("Preview of generated beat book:")
            print("─" * 80)
            print(beat_book[:500] + "..." if len(beat_book) > 500 else beat_book)
            print("─" * 80)
            
        else:
            print("\n❌ Failed to generate beat book")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
