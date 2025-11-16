#!/usr/bin/env python3
"""
LLM-powered Beat Book Creator
Uses Groq's gpt-oss-120b model to create a comprehensive source list
for an education reporter at the Easton Star-Democrat.

The LLM acts as a news editor onboarding a new reporter, with tools to:
- Search the Education.json file for context about people
- Perform web searches for contact info and additional details
- Generate a detailed beat book markdown document
"""

import json
import time
import subprocess
import re
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys


class GroqAgent:
    """LLM agent powered by Groq's gpt-oss-120b model"""
    
    def __init__(self, education_json_path: str, people_counts_path: str):
        self.education_json_path = Path(education_json_path)
        self.people_counts_path = Path(people_counts_path)
        self.max_retries = 5
        self.base_delay = 2  # seconds
        
        # Load data
        with open(self.education_json_path, 'r', encoding='utf-8') as f:
            self.education_data = json.load(f)
        
        with open(self.people_counts_path, 'r', encoding='utf-8') as f:
            self.people_counts_text = f.read()
    
    def call_groq_with_retry(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """
        Call Groq API with exponential backoff retry logic
        """
        for attempt in range(self.max_retries):
            try:
                # Use uv run llm with groq model
                cmd = [
                    'uv', 'run', 'llm',
                    '-m', 'groq/openai/gpt-oss-120b',
                    prompt
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180  # Longer timeout for complex prompts
                )
                
                if result.returncode == 0:
                    return result.stdout.strip()
                
                # Print actual error for debugging
                error_msg = result.stderr
                print(f"\n{'='*60}")
                print(f"Error from Groq API (attempt {attempt + 1}/{self.max_retries}):")
                print(f"{'='*60}")
                print(error_msg)
                print(f"{'='*60}\n")
                
                error_msg_lower = error_msg.lower()
                
                # Check for context/token limit errors
                if 'context' in error_msg_lower or 'token' in error_msg_lower or 'too long' in error_msg_lower or 'maximum' in error_msg_lower:
                    print("⚠️  This appears to be a CONTEXT/TOKEN LIMIT error, not a rate limit!")
                    print("The prompt is too long for the model's context window.")
                    return None
                
                # Check for rate limit error
                if 'rate' in error_msg_lower or 'limit' in error_msg_lower or '429' in error_msg_lower:
                    delay = self.base_delay * (2 ** attempt)
                    print(f"Rate limit detected. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                
                # Other errors - try again with backoff
                print(f"Unexpected error. Retrying with backoff...")
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt))
                    continue
                
            except subprocess.TimeoutExpired:
                print(f"Timeout calling Groq API (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay)
                    continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay)
                    continue
        
        print("Failed to get response after all retries")
        return None
    
    def search_education_json(self, person_name: str) -> List[Dict[str, Any]]:
        """
        Tool: Search Education.json for articles mentioning a specific person
        """
        results = []
        person_name_lower = person_name.lower()
        
        for article in self.education_data:
            content = article.get('content', '').lower()
            title = article.get('title', '').lower()
            
            if person_name_lower in content or person_name_lower in title:
                results.append({
                    'title': article.get('title', ''),
                    'date': article.get('date', ''),
                    'author': article.get('author', ''),
                    'content_excerpt': article.get('content', '')[:800]  # Increased to 800 chars for more context
                })
        
        return results
    
    def web_search_contact_info(self, person_name: str, organization: str) -> str:
        """
        Search for contact information by checking school district websites
        """
        try:
            # Map organizations to their likely website domains
            org_lower = organization.lower()
            
            # Try to determine the domain
            domain = None
            if 'talbot' in org_lower and 'public schools' in org_lower:
                domain = 'https://www.talbotschools.org'
            elif 'caroline' in org_lower and 'public schools' in org_lower:
                domain = 'https://www.carolineschools.org'  
            elif 'dorchester' in org_lower and 'public schools' in org_lower:
                domain = 'https://www.dorchesterschools.org'
            elif 'benedictine' in org_lower:
                domain = 'https://www.benedictineschool.org'
            
            if not domain:
                return "[Unable to determine organization website]"
            
            # Try to fetch staff directory or contact page
            search_paths = ['/staff', '/contact', '/administration', '/directory', '/about-us/staff']
            
            for path in search_paths:
                try:
                    cmd = ['curl', '-s', '-L', '--max-time', '5', f'{domain}{path}']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
                    
                    if result.returncode == 0 and result.stdout:
                        # Look for email addresses
                        import re
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', result.stdout)
                        
                        # Filter for relevant emails (exclude common non-personal emails)
                        filtered = [e for e in emails if not any(x in e.lower() for x in [
                            'webmaster', 'admin@', 'info@', 'contact@', 'support@', 'noreply'
                        ])]
                        
                        # Look specifically for the person's name in the page
                        name_parts = person_name.lower().replace('dr.', '').replace('dr', '').strip().split()
                        for email in filtered:
                            email_local = email.split('@')[0].lower()
                            # Check if name parts appear in email
                            if any(part in email_local for part in name_parts if len(part) > 2):
                                return f"Found via {domain}{path}: {email}"
                        
                        # If we found any relevant emails, return the first few
                        if filtered:
                            return f"Emails from {domain}{path}: {', '.join(filtered[:3])} [Verify which is correct]"
                
                except:
                    continue
            
            return f"[Checked {domain} but no contact info found]"
            
        except Exception as e:
            return f"[Web search error: {str(e)[:50]}]"
    
    def web_search(self, query: str) -> str:
        """
        Tool: Perform web search using ddg (DuckDuckGo) via llm
        Falls back to simple search if ddg not available
        """
        try:
            # Try using ddg search if available
            cmd = ['ddg', query, '-n', '3']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            # Fallback: return a note that web search would be performed
            return f"[Web search for: {query}]"
            
        except Exception as e:
            return f"[Web search unavailable: {query}]"
    
    def get_top_people(self, n: int = 50) -> List[str]:
        """Extract top N people from the counts file"""
        people = []
        lines = self.people_counts_text.split('\n')
        
        for line in lines:
            if ':' in line and not line.startswith('=') and 'Total' not in line:
                match = re.match(r'^(.+?):\s*(\d+)', line)
                if match:
                    people.append(match.group(1).strip())
                    if len(people) >= n:
                        break
        
        return people
    
    def research_person(self, person_name: str) -> Dict[str, Any]:
        """
        Research a person using available tools - now extracts ALL mentions
        """
        print(f"  Researching: {person_name}...")
        
        # Search Education.json - get ALL articles
        articles = self.search_education_json(person_name)
        
        # Extract comprehensive information from all articles
        all_mentions = []
        roles_found = set()
        organizations_found = set()
        quotes = []
        topics = set()
        
        for article in articles:
            # Extract context around the person's name
            content = article['content_excerpt']
            content_lower = content.lower()
            name_lower = person_name.lower()
            
            # Find all occurrences of the name in this article
            idx = 0
            while True:
                idx = content_lower.find(name_lower, idx)
                if idx == -1:
                    break
                
                # Extract context around mention (300 chars before and after)
                start = max(0, idx - 300)
                end = min(len(content), idx + len(person_name) + 300)
                context = content[start:end]
                
                # Look for role indicators in context
                role_patterns = [
                    'superintendent', 'principal', 'teacher', 'director', 
                    'president', 'board member', 'commissioner', 'governor',
                    'administrator', 'coordinator', 'executive', 'chair',
                    'vice president', 'assistant', 'manager', 'officer'
                ]
                
                for pattern in role_patterns:
                    if pattern in context.lower():
                        # Try to extract the full title
                        roles_found.add(pattern.title())
                
                # Look for organization mentions
                org_patterns = [
                    'county public schools', 'board of education', 'college',
                    'school district', 'department of education', 'university'
                ]
                
                for pattern in org_patterns:
                    if pattern in context.lower():
                        # Extract a bit more context to get the full org name
                        for word in context.split():
                            if pattern.split()[0] in word.lower():
                                organizations_found.add(pattern.title())
                
                idx += len(person_name)
            
            # Look for direct quotes (text in quotation marks near their name)
            quote_pattern_single = r'"([^"]{20,200})"'
            quote_pattern_double = r'"([^"]{20,200})"'
            
            import re
            for match in re.finditer(quote_pattern_single, content):
                quote_text = match.group(1)
                # Check if the person's name is within 200 chars of this quote
                quote_pos = match.start()
                name_positions = [m.start() for m in re.finditer(re.escape(person_name), content, re.IGNORECASE)]
                for name_pos in name_positions:
                    if abs(quote_pos - name_pos) < 200:
                        quotes.append({
                            'quote': quote_text,
                            'article': article['title'],
                            'date': article['date']
                        })
                        break
        
        research = {
            'name': person_name,
            'article_count': len(articles),
            'articles': articles,  # Keep ALL articles now
            'roles_detected': list(roles_found),
            'organizations_detected': list(organizations_found),
            'quotes_found': quotes[:5]  # Top 5 quotes
        }
        
        # Try to find contact info via web search if we have an organization
        if organizations_found:
            primary_org = list(organizations_found)[0]
            contact_info = self.web_search_contact_info(person_name, primary_org)
            research['web_search_contact'] = contact_info
        
        # Small delay to avoid hammering the system
        time.sleep(0.3)
        
        return research
    
    def create_beat_book(self, top_n: int = 12):
        """
        Create a beat book by having the LLM research and document sources
        """
        print("Starting beat book creation...")
        print(f"Researching top {top_n} people mentioned in education coverage...")
        
        # Get top people
        top_people = self.get_top_people(top_n)
        
        # Research each person
        all_research = []
        for i, person in enumerate(top_people, 1):
            print(f"[{i}/{len(top_people)}] ", end='')
            research = self.research_person(person)
            all_research.append(research)
        
        print("\nGenerating beat book with LLM...")
        
        # Create comprehensive prompt for the LLM
        prompt = self._create_beat_book_prompt(all_research)
        
        # Show prompt stats
        prompt_length = len(prompt)
        prompt_tokens_estimate = prompt_length // 4  # Rough estimate: ~4 chars per token
        print(f"Prompt length: {prompt_length:,} characters (~{prompt_tokens_estimate:,} tokens estimated)")
        
        if prompt_tokens_estimate > 100000:
            print("⚠️  WARNING: Prompt may be too long for context window!")
            print("Consider reducing the number of people researched.")
        
        # Get LLM response
        beat_book_content = self.call_groq_with_retry(prompt, max_tokens=8000)
        
        if not beat_book_content:
            print("Failed to generate beat book content")
            return None
        
        # Find next version number
        version = self._get_next_version()
        
        # Save beat book
        output_file = Path(self.education_json_path).parent / f"beat_book_v{version}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(beat_book_content)
        
        print(f"\n✓ Beat book created: {output_file}")
        return output_file
    
    def _get_next_version(self) -> int:
        """Find the next available version number for beat book"""
        existing_files = list(Path(self.education_json_path).parent.glob("beat_book_v*.md"))
        
        if not existing_files:
            return 1
        
        versions = []
        for f in existing_files:
            match = re.search(r'beat_book_v(\d+)\.md', f.name)
            if match:
                versions.append(int(match.group(1)))
        
        return max(versions) + 1 if versions else 1
    
    def _create_beat_book_prompt(self, research_data: List[Dict[str, Any]]) -> str:
        """Create the prompt for the LLM to generate the beat book"""
        
        # Build research summary with comprehensive analysis
        research_summary = []
        for person in research_data:
            name = person['name']
            count = person['article_count']
            
            summary = f"\n### {name}\n"
            summary += f"**Frequency:** Mentioned in {count} articles\n"
            
            # Add detected roles and organizations
            if person.get('roles_detected'):
                summary += f"**Roles detected across articles:** {', '.join(person['roles_detected'])}\n"
            
            if person.get('organizations_detected'):
                summary += f"**Organizations detected:** {', '.join(person['organizations_detected'])}\n"
            
            # Add quotes if found
            if person.get('quotes_found'):
                summary += f"\n**Direct quotes found:**\n"
                for q in person['quotes_found'][:3]:  # Top 3 quotes
                    summary += f"- \"{q['quote']}\" (from \"{q['article']}\", {q['date']})\n"
            
            # Add web search contact info if found
            if person.get('web_search_contact'):
                summary += f"\n**Web search contact info:**\n{person['web_search_contact']}\n"
            
            # Now show key articles (limit to top 5 to save tokens)
            if person['articles']:
                summary += f"\n**Key articles (showing {min(5, len(person['articles']))} of {len(person['articles'])}):**\n"
                for i, article in enumerate(person['articles'][:5], 1):
                    summary += f"\n{i}. \"{article['title']}\" ({article['date']})\n"
                    # Clean up and show meaningful excerpt
                    excerpt = ' '.join(article['content_excerpt'].split())[:400]
                    summary += f"   {excerpt}...\n"
            
            summary += "\n" + "="*60 + "\n"
            research_summary.append(summary)
        
        research_text = ''.join(research_summary)
        
        prompt = f"""You are a senior news editor at the Easton Star-Democrat, a local newspaper covering Maryland's Eastern Shore. You are creating a BEAT BOOK for a new education reporter.

CRITICAL INSTRUCTIONS - READ CAREFULLY:
- I have conducted COMPREHENSIVE research on each person, analyzing ALL articles where they appear
- For each person, I've detected potential roles and organizations by analyzing context across multiple articles
- CAREFULLY READ the detected roles and organizations - these are extracted from the actual text
- Cross-reference information across multiple articles to confirm consistent details
- Extract titles and roles that appear repeatedly or in formal contexts (like "Superintendent X announced..." or "Board President Y said...")
- DO NOT make up phone numbers or addresses
- Mark suggested contact info clearly as "[Suggested - verify before use]"
- Use the actual quotes provided to show the person's voice and perspective
- Synthesize information ACROSS articles - if someone is called "Superintendent" in 3 different articles, that's their confirmed role

COMPREHENSIVE RESEARCH DATA:
Below is detailed research from our archive. I've analyzed every article mentioning each person and extracted:
- Detected roles (patterns found across articles)
- Detected organizations (mentioned in context)
- Direct quotes (actual statements they made)
- Key article excerpts

{research_text}

YOUR TASK:
Create a beat book with entries for each person. For each entry, provide:

1. **Name** (exactly as found in articles)
2. **Role/Title** - Synthesize from the detected roles and article contexts. If multiple articles consistently refer to someone as "Superintendent" or "Board President," state that as their role. If genuinely unclear, note it.
3. **Organization** - Use the detected organizations and context
4. **What We Know** - Synthesize key facts across ALL their article appearances: what they've done, said, voted on, led, etc.
5. **Key Topics** - What issues they're connected to based on article analysis
6. **Quotes** - Include 1-2 actual quotes from the research (shows their voice)
7. **Contact Info** - I've conducted web searches for each person. Use the "Web search contact info" section if available. If actual contact info was found, include it. If not found, suggest likely email patterns based on organization, clearly marked as "[Suggested - verify before use]"
8. **Reporting Tips** - Based on their role and topics, suggest what angles to approach them about

CONTACT INFORMATION INSTRUCTIONS:
- If "Web search contact info" shows actual email addresses, INCLUDE THEM in the contact section
- Verify the emails look legitimate (proper domain for the organization)
- If no web search results, suggest standard patterns like firstname.lastname@organization.domain
- Always mark suggested (non-verified) contacts as "[Suggested - verify before use]"

FORMATTING:
- Title: "# Education Beat Book - Easton Star-Democrat"
- Subtitle: "## Compiled November 16, 2025"  
- Brief intro explaining this is based on comprehensive analysis
- Use ## for each person's entry
- Order by frequency (most mentioned first)
- Include disclaimer about verifying contact info

REMEMBER: You have COMPREHENSIVE data - use it! Synthesize across articles to build complete, factual profiles.

FORMATTING:
- Title: "# Education Beat Book - Easton Star-Democrat"
- Subtitle: "## Compiled November 16, 2025"
- Brief intro explaining this is based on article frequency analysis
- Use ## for each person's entry
- Order by frequency (most mentioned first)
- Include a disclaimer that all contact info needs verification

REMEMBER: Accuracy over completeness. If you don't see it in the excerpts, don't include it or clearly mark it as needing verification.

Generate the beat book now:"""

        return prompt


def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    education_json = script_dir / "Education.json"
    people_counts = script_dir / "people_counts.txt"
    
    # Verify files exist
    if not education_json.exists():
        print(f"Error: {education_json} not found")
        sys.exit(1)
    
    if not people_counts.exists():
        print(f"Error: {people_counts} not found")
        sys.exit(1)
    
    # Create agent
    agent = GroqAgent(
        education_json_path=str(education_json),
        people_counts_path=str(people_counts)
    )
    
    # Create beat book
    output_file = agent.create_beat_book(top_n=12)
    
    if output_file:
        print(f"\n{'='*60}")
        print("Beat book generation complete!")
        print(f"Output: {output_file}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
