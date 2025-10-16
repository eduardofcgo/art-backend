#!/usr/bin/env python3
"""
Simple test script for the Art Interpretation API
Usage: python test_api.py <path_to_image>
"""

import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os


def xml_to_html(xml_content: str, image_path: str) -> str:
    """Convert the XML interpretation to a beautiful HTML document with interactive artwork explorer"""

    try:
        root = ET.fromstring(xml_content.strip())
    except ET.ParseError as e:
        return f"<html><body><h1>Error parsing XML</h1><pre>{str(e)}</pre><pre>{xml_content}</pre></body></html>"

    # Extract title from XML
    title = root.find("title")
    title_text = title.text if title is not None else "Art Interpretation"

    # Extract spatial details
    details_element = root.find("details")
    spatial_details = []
    if details_element is not None:
        for detail in details_element.findall("detail"):
            spatial_details.append(
                {
                    "x": detail.get("x", "50"),
                    "y": detail.get("y", "50"),
                    "region": detail.get("region", ""),
                    "title": detail.get("title", "Detail"),
                    "description": detail.text or "",
                }
            )

    # Generate JSON for spatial details
    import json

    spatial_details_json = json.dumps(spatial_details)

    def process_content(element, level=0):
        """Process an element's content (text and inline tags like wikilink/image), excluding section children"""
        if element is None:
            return ""

        html_parts = []

        # Add text before first child
        if element.text:
            html_parts.append(element.text.strip())

        # Process children
        for child in element:
            if child.tag == "wikilink":
                term = child.text or ""
                wiki_url = f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}"
                html_parts.append(
                    f'<a href="{wiki_url}" target="_blank" class="wiki-link">{term}</a>'
                )
                # Add text after this child
                if child.tail:
                    html_parts.append(child.tail.strip())
            elif child.tag == "image":
                search_query = child.get("search", "")
                caption = child.text or ""
                google_search_url = f"https://www.google.com/search?tbm=isch&q={search_query.replace(' ', '+')}"
                html_parts.append(
                    f"""
                <div class="image-suggestion">
                    <div class="image-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            <circle cx="8.5" cy="8.5" r="1.5"></circle>
                            <polyline points="21 15 16 10 5 21"></polyline>
                        </svg>
                    </div>
                    <p class="image-caption">{caption}</p>
                    <a href="{google_search_url}" target="_blank" class="search-link">
                        Search: {search_query}
                    </a>
                </div>
                """
                )
                # Add text after this child
                if child.tail:
                    html_parts.append(child.tail.strip())
            elif child.tag == "section":
                # Don't process section tags here - they're handled separately
                # But we need to add the tail text
                if child.tail:
                    html_parts.append(child.tail.strip())

        content = " ".join(html_parts).strip()
        return f"<p>{content}</p>" if content else ""

    def process_section(section, level=1):
        """Recursively process a section element and its subsections"""
        section_name = section.get("name", "Untitled Section")
        html_parts = []

        # Determine heading level (h2 for top-level, h3 for subsections, etc.)
        heading_level = min(level + 1, 6)  # HTML only goes up to h6
        heading_class = f"section-h{heading_level}"

        # Add section heading
        html_parts.append(
            f'<h{heading_level} class="{heading_class}">{section_name}</h{heading_level}>'
        )

        # Add section content (text and inline elements, excluding subsections)
        content = process_content(section, level)
        if content:
            html_parts.append(content)

        # Process subsections recursively
        subsections = section.findall("section")
        if subsections:
            html_parts.append('<div class="subsections">')
            for subsection in subsections:
                html_parts.append(process_section(subsection, level + 1))
            html_parts.append("</div>")

        return "\n".join(html_parts)

    # Process all top-level sections
    sections_html = []
    for section in root.findall("section"):
        section_html = (
            f'<section class="main-section">\n{process_section(section, 1)}\n</section>'
        )
        sections_html.append(section_html)

    # Convert image to base64 for embedding
    import base64

    try:
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode()
            image_ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }.get(image_ext, "image/jpeg")
            embedded_image = f"data:{mime_type};base64,{image_data}"
    except:
        embedded_image = ""

    # Create HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_text}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
            letter-spacing: 2px;
        }}
        
        .meta {{
            font-size: 0.9em;
            opacity: 0.9;
            font-family: 'Arial', sans-serif;
        }}
        
        .content {{
            padding: 50px;
        }}
        
        .main-section {{
            margin-bottom: 40px;
        }}
        
        h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #f0f0f0;
            font-weight: 400;
        }}
        
        h3 {{
            color: #764ba2;
            font-size: 1.4em;
            margin-top: 25px;
            margin-bottom: 15px;
            font-weight: 400;
        }}
        
        h4 {{
            color: #8b5fbf;
            font-size: 1.2em;
            margin-top: 20px;
            margin-bottom: 12px;
            font-weight: 400;
        }}
        
        h5, h6 {{
            color: #9d7ac7;
            font-size: 1.1em;
            margin-top: 15px;
            margin-bottom: 10px;
            font-weight: 400;
        }}
        
        .subsections {{
            margin-left: 20px;
            margin-top: 15px;
            padding-left: 20px;
            border-left: 2px solid #e8e8f0;
        }}
        
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        .wiki-link {{
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px dotted #667eea;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .wiki-link:hover {{
            color: #764ba2;
            border-bottom: 1px solid #764ba2;
            background-color: #f8f9ff;
        }}
        
        .image-suggestion {{
            background: #f8f9ff;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            transition: transform 0.3s ease;
        }}
        
        .image-suggestion:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }}
        
        .image-placeholder {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 12px;
        }}
        
        .image-placeholder svg {{
            width: 32px;
            height: 32px;
        }}
        
        .image-caption {{
            font-style: italic;
            color: #555;
            margin-bottom: 8px;
            font-size: 0.95em;
        }}
        
        .search-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
            font-family: 'Arial', sans-serif;
            padding: 6px 12px;
            border: 1px solid #667eea;
            border-radius: 4px;
            transition: all 0.3s ease;
        }}
        
        .search-link:hover {{
            background: #667eea;
            color: white;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 20px 50px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            font-family: 'Arial', sans-serif;
            border-top: 1px solid #e0e0e0;
        }}
        
        /* Interactive Artwork Explorer Styles */
        .artwork-explorer {{
            background: #f8f9ff;
            padding: 40px;
            margin-bottom: 40px;
            border-radius: 12px;
        }}
        
        .explorer-title {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 400;
        }}
        
        .explorer-container {{
            display: flex;
            gap: 30px;
            align-items: flex-start;
        }}
        
        .artwork-container {{
            flex: 1;
            position: relative;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        
        .artwork-image {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        .hotspot {{
            position: absolute;
            width: 24px;
            height: 24px;
            margin-left: -12px;
            margin-top: -12px;
            background: rgba(102, 126, 234, 0.9);
            border: 3px solid white;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            animation: pulse 2s infinite;
            z-index: 10;
        }}
        
        .hotspot:hover {{
            background: rgba(118, 75, 162, 1);
            transform: scale(1.3);
            animation: none;
        }}
        
        .hotspot.active {{
            background: rgba(118, 75, 162, 1);
            transform: scale(1.3);
            animation: none;
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
            }}
            50% {{
                box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
            }}
        }}
        
        .hotspot-number {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 11px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        }}
        
        .detail-panel {{
            flex: 0 0 350px;
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .detail-panel.empty {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-style: italic;
            text-align: center;
        }}
        
        .detail-title {{
            color: #667eea;
            font-size: 1.3em;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        
        .detail-region {{
            color: #999;
            font-size: 0.9em;
            font-family: Arial, sans-serif;
            margin-bottom: 15px;
            text-transform: capitalize;
        }}
        
        .detail-description {{
            line-height: 1.8;
            color: #2c3e50;
        }}
        
        .explorer-instructions {{
            text-align: center;
            color: #666;
            font-size: 0.95em;
            margin-top: 20px;
            font-family: Arial, sans-serif;
        }}
        
        @media (max-width: 1024px) {{
            .explorer-container {{
                flex-direction: column;
            }}
            
            .detail-panel {{
                flex: 1;
                width: 100%;
                max-height: none;
            }}
        }}
        
        @media (max-width: 768px) {{
            .content {{
                padding: 30px 20px;
            }}
            
            header {{
                padding: 30px 20px;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
            
            h2 {{
                font-size: 1.4em;
            }}
            
            h3 {{
                font-size: 1.2em;
            }}
            
            .subsections {{
                margin-left: 10px;
                padding-left: 10px;
            }}
            
            .artwork-explorer {{
                padding: 20px;
            }}
            
            .explorer-title {{
                font-size: 1.4em;
            }}
            
            .detail-panel {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title_text}</h1>
            <p class="meta">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p class="meta">Source: {os.path.basename(image_path)}</p>
        </header>
        
        <div class="content">
            {('<!-- Interactive Artwork Explorer -->' + chr(10) +
            '<div class="artwork-explorer">' + chr(10) +
            '    <h2 class="explorer-title">Explore the Artwork</h2>' + chr(10) +
            '    <div class="explorer-container">' + chr(10) +
            '        <div class="artwork-container" id="artworkContainer">' + chr(10) +
            '            <img src="' + embedded_image + '" alt="Artwork" class="artwork-image" id="artworkImage">' + chr(10) +
            '        </div>' + chr(10) +
            '        <div class="detail-panel empty" id="detailPanel">' + chr(10) +
            '            <p>Click on any numbered point on the artwork to explore specific details</p>' + chr(10) +
            '        </div>' + chr(10) +
            '    </div>' + chr(10) +
            '    <p class="explorer-instructions">💡 Hover over or click the numbered points to discover details about specific areas of the artwork</p>' + chr(10) +
            '</div>' + chr(10)) if spatial_details else ''}
            
            {chr(10).join(sections_html)}
        </div>
        
        <footer>
            <p>Art Interpretation powered by AI | 
            <a href="https://en.wikipedia.org" target="_blank" style="color: #667eea; text-decoration: none;">Wikipedia links</a> provided for reference</p>
        </footer>
    </div>
    
    <script>
        // Spatial details data
        const spatialDetails = {spatial_details_json};
        
        // Initialize artwork explorer
        function initializeExplorer() {{
            if (!spatialDetails || spatialDetails.length === 0) {{
                return;
            }}
            
            const container = document.getElementById('artworkContainer');
            const image = document.getElementById('artworkImage');
            const detailPanel = document.getElementById('detailPanel');
            
            // Wait for image to load
            image.onload = function() {{
                // Create hotspots
                spatialDetails.forEach((detail, index) => {{
                    const hotspot = document.createElement('div');
                    hotspot.className = 'hotspot';
                    hotspot.style.left = detail.x + '%';
                    hotspot.style.top = detail.y + '%';
                    hotspot.dataset.index = index;
                    
                    const number = document.createElement('span');
                    number.className = 'hotspot-number';
                    number.textContent = index + 1;
                    hotspot.appendChild(number);
                    
                    // Click event
                    hotspot.addEventListener('click', function() {{
                        showDetail(index);
                        // Remove active class from all hotspots
                        document.querySelectorAll('.hotspot').forEach(h => h.classList.remove('active'));
                        // Add active class to clicked hotspot
                        this.classList.add('active');
                    }});
                    
                    // Hover event
                    hotspot.addEventListener('mouseenter', function() {{
                        if (!this.classList.contains('active')) {{
                            showDetail(index);
                        }}
                    }});
                    
                    container.appendChild(hotspot);
                }});
            }};
            
            // Trigger load if already cached
            if (image.complete) {{
                image.onload();
            }}
        }}
        
        // Show detail in panel
        function showDetail(index) {{
            const detail = spatialDetails[index];
            const detailPanel = document.getElementById('detailPanel');
            
            detailPanel.classList.remove('empty');
            detailPanel.innerHTML = `
                <div class="detail-title">${{detail.title}}</div>
                <div class="detail-region">📍 ${{detail.region}}</div>
                <div class="detail-description">${{detail.description}}</div>
            `;
        }}
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', initializeExplorer);
    </script>
</body>
</html>
"""
    return html


def test_interpret_art(image_path: str, api_url: str = "http://localhost:8000"):
    """Test the art interpretation endpoint"""

    endpoint = f"{api_url}/api/ai/artwork/explain"

    print(f"Testing art interpretation API...")
    print(f"Image: {image_path}")
    print(f"Endpoint: {endpoint}\n")

    try:
        with open(image_path, "rb") as image_file:
            files = {"data": image_file}
            response = requests.post(endpoint, files=files)

        if response.status_code == 200:
            xml_content = response.text
            print("✅ Success! Received XML interpretation\n")

            # Convert XML to HTML
            html_content = xml_to_html(xml_content, image_path)

            # Generate output filenames (same base name, different extensions)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"interpretation_{base_name}_{timestamp}"
            html_filename = f"{base_filename}.html"
            xml_filename = f"{base_filename}.xml"

            # Save HTML file
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Save XML file
            with open(xml_filename, "w", encoding="utf-8") as f:
                f.write(xml_content)

            print("=" * 80)
            print(f"📄 HTML interpretation saved to: {html_filename}")
            print(f"📄 Raw XML saved to: {xml_filename}")
            print("=" * 80)
            print("\nXML Preview:")
            print("-" * 80)
            # Print first 500 chars of XML
            print(xml_content[:500] + "..." if len(xml_content) > 500 else xml_content)
            print("-" * 80)
            print(
                f"\n✨ Open {html_filename} in your browser to view the formatted interpretation!"
            )

        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(response.text)

    except FileNotFoundError:
        print(f"❌ Error: Image file not found: {image_path}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to API at {api_url}")
        print("Make sure the server is running with: uvicorn app:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    # Then test art interpretation if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <path_to_image>")
        print("Example: python test_api.py artwork.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    test_interpret_art(image_path)
