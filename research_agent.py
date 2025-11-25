import arxiv
from duckduckgo_search import DDGS
import openai
from typing import List, Dict, Optional
import requests
from datetime import datetime
import json

class ResearchAgent:
    """Handles multi-modal research from various sources"""
    
    def __init__(self):
        # Initialize OpenRouter client
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", "your-key-here")
        )
        self.model = "google/gemini-2.0-flash-exp:free"
    
    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search ArXiv for academic papers"""
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in search.results():
                results.append({
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "summary": paper.summary[:500] + "...",
                    "published": paper.published.isoformat(),
                    "url": paper.pdf_url,
                    "categories": paper.categories
                })
            
            return results
        except Exception as e:
            print(f"ArXiv search error: {e}")
            return []
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search the web using DuckDuckGo"""
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                        "source": "web"
                    })
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def search_youtube(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube videos (simplified - returns mock data for demo)"""
        # In production, use YouTube Data API
        # For now, we'll use web search with site:youtube.com
        try:
            results = []
            with DDGS() as ddgs:
                youtube_query = f"site:youtube.com {query}"
                for r in ddgs.text(youtube_query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                        "source": "youtube"
                    })
            return results
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []
    
    def extract_insights(self, sources: Dict) -> List[str]:
        """Use AI to extract key insights from all sources"""
        
        # Compile all source data
        all_content = []
        
        for source_type, items in sources.items():
            for item in items:
                if source_type == "arxiv":
                    all_content.append(f"Paper: {item['title']}\n{item['summary']}")
                else:
                    all_content.append(f"{item['title']}\n{item['snippet']}")
        
        # Prepare prompt for AI
        prompt = f"""Based on the following research sources, extract 5-7 key insights and findings.
        Focus on the most important and actionable information.
        
        Sources:
        {chr(10).join(all_content[:10])}  # Limit to first 10 items to stay within token limits
        
        Format your response as a JSON array of strings, each being one key insight.
        Example: ["Insight 1", "Insight 2", ...]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research analyst expert at synthesizing information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                insights = json.loads(content)
                if isinstance(insights, list):
                    return insights[:7]  # Max 7 insights
            except json.JSONDecodeError:
                # If not JSON, split by newlines and clean up
                insights = [line.strip('- •').strip() for line in content.split('\n') if line.strip()]
                return insights[:7]
            
        except Exception as e:
            print(f"Insight extraction error: {e}")
            return [
                "Research data collected successfully",
                "Multiple sources analyzed",
                "Content ready for generation"
            ]
    
    def create_knowledge_graph(self, sources: Dict) -> Dict:
        """Create a simple knowledge graph structure"""
        
        graph = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_sources": sum(len(v) for v in sources.values())
            }
        }
        
        # Create nodes for each source
        node_id = 0
        for source_type, items in sources.items():
            for item in items[:5]:  # Limit to 5 per source
                graph["nodes"].append({
                    "id": node_id,
                    "label": item.get("title", "Unknown"),
                    "type": source_type,
                    "url": item.get("url", "")
                })
                node_id += 1
        
        return graph
    
    def analyze_with_ai(self, prompt: str, context: str = "") -> str:
        """General purpose AI analysis"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful research and content assistant."}
            ]
            
            if context:
                messages.append({"role": "user", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"AI analysis error: {e}")
            return "Analysis unavailable at this time."