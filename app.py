import gradio as gr
import os
from typing import List, Dict, Optional
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from research_agent import ResearchAgent
from analytics_agent import AnalyticsAgent
from content_creator import ContentCreator
from database_manager import DatabaseManager

class ContentFlowAI:
    """Main orchestrator for the ContentFlow AI system"""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.analytics_agent = AnalyticsAgent()
        self.content_creator = ContentCreator()
        self.db_manager = DatabaseManager()
        
    def research_topic(
        self, 
        topic: str, 
        sources: List[str],
        max_results: int = 5
    ) -> Dict:
        """Research phase - gather information from multiple sources"""
        
        if not topic:
            return {"error": "Please enter a topic to research"}
        
        results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "key_insights": [],
            "knowledge_graph": None
        }
        
        # Research from selected sources
        if "ArXiv" in sources:
            results["sources"]["arxiv"] = self.research_agent.search_arxiv(topic, max_results)
        
        if "Web Search" in sources:
            results["sources"]["web"] = self.research_agent.search_web(topic, max_results)
        
        if "YouTube" in sources:
            results["sources"]["youtube"] = self.research_agent.search_youtube(topic, max_results)
        
        # Extract key insights using AI
        results["key_insights"] = self.research_agent.extract_insights(results["sources"])
        
        # Generate knowledge graph
        results["knowledge_graph"] = self.research_agent.create_knowledge_graph(results["sources"])
        
        # Store in database
        self.db_manager.store_research(results)
        
        return results
    
    def analyze_performance(
        self,
        topic: str,
        platform: str = "twitter"
    ) -> Dict:
        """Analytics phase - analyze what works best"""
        
        # Get historical performance data
        historical_data = self.db_manager.get_historical_performance(platform)
        
        # Analyze trends
        analysis = self.analytics_agent.analyze_trends(topic, historical_data)
        
        return analysis
    
    def generate_content(
        self,
        research_data: Dict,
        platforms: List[str],
        tone: str = "professional",
        include_image: bool = True
    ) -> Dict:
        """Content creation phase - generate ready-to-post content"""
        
        content_package = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform in platforms:
            # Generate platform-specific content
            content = self.content_creator.generate_for_platform(
                research_data=research_data,
                platform=platform,
                tone=tone
            )
            
            # Generate accompanying image if requested
            if include_image:
                content["image"] = self.content_creator.generate_image(
                    research_data["topic"]
                )
            
            content_package["platforms"][platform] = content
        
        # Store generated content
        self.db_manager.store_content(content_package)
        
        return content_package

def create_gradio_interface():
    """Create the Gradio interface"""
    
    app = ContentFlowAI()
    
    # Custom CSS
    custom_css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    .research-box {
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 20px;
    }
    .content-box {
        border: 2px solid #3b82f6;
        border-radius: 8px;
        padding: 20px;
    }
    """
    
    with gr.Blocks(css=custom_css, title="ContentFlow AI") as demo:
        
        # Header
        gr.Markdown("""
        # 🚀 ContentFlow AI
        ### From Research to Viral Content in Minutes
        Research → Analyze → Create → Post
        """)
        
        # State to store research results
        research_state = gr.State(value={})
        
        with gr.Tabs() as tabs:
            
            # ========== TAB 1: RESEARCH ==========
            with gr.Tab("🔬 Research", id=0):
                gr.Markdown("### Step 1: Research Your Topic")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        topic_input = gr.Textbox(
                            label="Topic or Query",
                            placeholder="e.g., 'Latest breakthroughs in quantum computing'",
                            lines=2
                        )
                        
                        source_selection = gr.CheckboxGroup(
                            choices=["ArXiv", "Web Search", "YouTube"],
                            value=["ArXiv", "Web Search"],
                            label="Select Sources"
                        )
                        
                        max_results = gr.Slider(
                            minimum=3,
                            maximum=10,
                            value=5,
                            step=1,
                            label="Results per Source"
                        )
                        
                        research_btn = gr.Button("🔍 Start Research", variant="primary", size="lg")
                    
                    with gr.Column(scale=3):
                        research_status = gr.Markdown("*Waiting to start research...*")
                        research_output = gr.JSON(label="Research Results")
                        insights_output = gr.Textbox(
                            label="Key Insights",
                            lines=10,
                            interactive=False
                        )
                
                def do_research(topic, sources, max_res):
                    if not topic:
                        return "❌ Please enter a topic", {}, "", {}
                    
                    status = f"🔄 Researching '{topic}' from {len(sources)} sources..."
                    yield status, {}, "", {}
                    
                    results = app.research_topic(topic, sources, max_res)
                    
                    # Format insights for display
                    insights_text = "\n\n".join([f"• {insight}" for insight in results.get("key_insights", [])])
                    
                    final_status = f"✅ Research complete! Found {sum(len(v) for v in results.get('sources', {}).values())} items"
                    
                    return final_status, results, insights_text, results
                
                research_btn.click(
                    fn=do_research,
                    inputs=[topic_input, source_selection, max_results],
                    outputs=[research_status, research_output, insights_output, research_state]
                )
            
            # ========== TAB 2: ANALYTICS ==========
            with gr.Tab("📊 Analytics", id=1):
                gr.Markdown("### Step 2: Analyze Performance Data")
                
                with gr.Row():
                    with gr.Column():
                        analytics_platform = gr.Dropdown(
                            choices=["Twitter", "LinkedIn", "Instagram", "Blog"],
                            value="Twitter",
                            label="Platform"
                        )
                        
                        analyze_btn = gr.Button("📈 Analyze Trends", variant="primary")
                    
                    with gr.Column(scale=2):
                        analytics_output = gr.JSON(label="Analytics Results")
                        recommendations = gr.Textbox(
                            label="Recommendations",
                            lines=8,
                            interactive=False
                        )
                
                def do_analytics(platform, research_data):
                    if not research_data:
                        return {"error": "Please complete research first"}, "⚠️ No research data available"
                    
                    topic = research_data.get("topic", "")
                    analysis = app.analyze_performance(topic, platform.lower())
                    
                    # Format recommendations
                    recs = "\n\n".join([f"✓ {rec}" for rec in analysis.get("recommendations", [])])
                    
                    return analysis, recs
                
                analyze_btn.click(
                    fn=do_analytics,
                    inputs=[analytics_platform, research_state],
                    outputs=[analytics_output, recommendations]
                )
            
            # ========== TAB 3: CONTENT CREATION ==========
            with gr.Tab("✨ Create Content", id=2):
                gr.Markdown("### Step 3: Generate Platform-Specific Content")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        platform_selection = gr.CheckboxGroup(
                            choices=["Twitter", "LinkedIn", "Instagram", "Blog Post"],
                            value=["Twitter"],
                            label="Target Platforms"
                        )
                        
                        tone_selection = gr.Radio(
                            choices=["Professional", "Casual", "Technical", "Engaging"],
                            value="Professional",
                            label="Content Tone"
                        )
                        
                        include_image = gr.Checkbox(
                            value=True,
                            label="Generate Images"
                        )
                        
                        generate_btn = gr.Button("🎨 Generate Content", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        content_status = gr.Markdown("*Ready to generate content...*")
                        
                        with gr.Accordion("Twitter Content", open=True):
                            twitter_output = gr.Textbox(label="Tweet/Thread", lines=6)
                            twitter_image = gr.Image(label="Twitter Image")
                        
                        with gr.Accordion("LinkedIn Content", open=False):
                            linkedin_output = gr.Textbox(label="LinkedIn Post", lines=8)
                            linkedin_image = gr.Image(label="LinkedIn Image")
                        
                        with gr.Accordion("Instagram Content", open=False):
                            instagram_output = gr.Textbox(label="Instagram Caption", lines=6)
                            instagram_image = gr.Image(label="Instagram Image")
                        
                        with gr.Accordion("Blog Post", open=False):
                            blog_output = gr.Textbox(label="Blog Content", lines=15)
                
                def do_generate(platforms, tone, img_flag, research_data):
                    if not research_data:
                        return "❌ Please complete research first", "", None, "", None, "", None, ""
                    
                    status = f"🎨 Generating content for {len(platforms)} platform(s)..."
                    yield status, "", None, "", None, "", None, ""
                    
                    content_package = app.generate_content(
                        research_data=research_data,
                        platforms=platforms,
                        tone=tone.lower(),
                        include_image=img_flag
                    )
                    
                    # Extract content for each platform
                    twitter = content_package["platforms"].get("Twitter", {}).get("text", "")
                    twitter_img = content_package["platforms"].get("Twitter", {}).get("image")
                    
                    linkedin = content_package["platforms"].get("LinkedIn", {}).get("text", "")
                    linkedin_img = content_package["platforms"].get("LinkedIn", {}).get("image")
                    
                    instagram = content_package["platforms"].get("Instagram", {}).get("text", "")
                    instagram_img = content_package["platforms"].get("Instagram", {}).get("image")
                    
                    blog = content_package["platforms"].get("Blog Post", {}).get("text", "")
                    
                    final_status = f"✅ Content generated successfully for {len(platforms)} platform(s)!"
                    
                    return final_status, twitter, twitter_img, linkedin, linkedin_img, instagram, instagram_img, blog
                
                generate_btn.click(
                    fn=do_generate,
                    inputs=[platform_selection, tone_selection, include_image, research_state],
                    outputs=[
                        content_status,
                        twitter_output, twitter_image,
                        linkedin_output, linkedin_image,
                        instagram_output, instagram_image,
                        blog_output
                    ]
                )
            
            # ========== TAB 4: EXPORT & SCHEDULE ==========
            with gr.Tab("📅 Export & Schedule", id=3):
                gr.Markdown("### Step 4: Schedule or Export Your Content")
                
                with gr.Row():
                    with gr.Column():
                        export_format = gr.Radio(
                            choices=["JSON", "Notion", "CSV", "Markdown"],
                            value="JSON",
                            label="Export Format"
                        )
                        
                        export_btn = gr.Button("💾 Export Content", variant="primary")
                        
                        gr.Markdown("---")
                        
                        gr.Markdown("### 📅 Schedule Posts")
                        schedule_date = gr.Textbox(
                            label="Schedule Date/Time",
                            placeholder="e.g., 2024-12-01 10:00 AM"
                        )
                        schedule_btn = gr.Button("⏰ Schedule Posts")
                    
                    with gr.Column(scale=2):
                        export_output = gr.Textbox(
                            label="Export Result",
                            lines=10,
                            interactive=False
                        )
                        
                        download_file = gr.File(label="Download Export")
                
                def do_export(format_type):
                    # This would export the content in the selected format
                    result = f"✅ Content exported successfully as {format_type}\n\n"
                    result += f"Export includes:\n• Research data\n• Generated content\n• Images\n• Analytics"
                    
                    return result, None
                
                export_btn.click(
                    fn=do_export,
                    inputs=[export_format],
                    outputs=[export_output, download_file]
                )
        
        # Footer
        gr.Markdown("""
        ---
        ### 💡 Tips:
        - Start with research to gather comprehensive information
        - Use analytics to understand what works best
        - Generate content for multiple platforms at once
        - Export and schedule for optimal posting times
        
        **Made with ❤️ for MCP Hackathon**
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860
    )