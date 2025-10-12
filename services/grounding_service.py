"""
Grounding DINO service for spatial localization using Replicate API.
"""

import base64
from typing import List, Dict, Optional


class GroundingDINOService:
    """Service for localizing elements in artworks using Grounding DINO on Replicate."""
    
    def __init__(self, api_token: str):
        """
        Initialize the Grounding DINO service.
        
        Args:
            api_token: Replicate API token from settings.
        """
        if not api_token:
            raise ValueError(
                "Replicate API token not found. Set REPLICATE_API_TOKEN in your .env file."
            )
        self.api_token = api_token
    
    def localize_queries(
        self, 
        image_path: str, 
        queries: List[Dict[str, str]],
        box_threshold: float = 0.25,
        text_threshold: float = 0.25
    ) -> List[Dict]:
        """
        Localize multiple queries in an image using Grounding DINO.
        
        Args:
            image_path: Path to the image file
            queries: List of dicts with 'query', 'title', and 'id' keys
            box_threshold: Confidence threshold for box detection (0-1)
            text_threshold: Confidence threshold for text matching (0-1)
            
        Returns:
            List of dicts with localization results containing:
                - id: Original query ID
                - title: Detail title
                - query: Original query text
                - x: Center x coordinate (percentage 0-100)
                - y: Center y coordinate (percentage 0-100)
                - confidence: Detection confidence score
                - box: Bounding box coordinates
        """
        try:
            import replicate
        except ImportError:
            raise ImportError(
                "replicate package not installed. Install with: pip install replicate"
            )
        
        # Configure Replicate client with API token
        client = replicate.Client(api_token=self.api_token)
        
        # Read and encode image, and get dimensions
        from PIL import Image
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        image_uri = f"data:image/jpeg;base64,{image_data}"
        
        results = []
        
        for query_data in queries:
            query_text = query_data["query"]
            
            try:
                # Call Grounding DINO API
                output = client.run(
                    "adirik/grounding-dino:efd10a8ddc57ea28773327e881ce95e20cc1d734c589f7dd01d2036921ed78aa",
                    input={
                        "image": image_uri,
                        "query": query_text,
                        "box_threshold": box_threshold,
                        "text_threshold": text_threshold
                    }
                )
                
                # Debug: Check output type (uncomment to debug)
                # print(f"DEBUG [{query_text}] - Output type: {type(output)}")
                # if isinstance(output, (str, dict, list)):
                #     print(f"  Content preview: {str(output)[:200]}")
                
                # Parse output - format varies by model version
                if output:
                    # Check if output is a dict with detections
                    if isinstance(output, dict):
                        detections = output.get("detections", [])
                    # Check if output is a list
                    elif isinstance(output, list) and len(output) > 0:
                        detections = output
                    else:
                        detections = []
                    
                    if detections and len(detections) > 0:
                        # Get the highest confidence detection
                        best_detection = None
                        for det in detections:
                            if isinstance(det, dict):
                                # Try both 'confidence' and 'score' keys
                                det_conf = det.get("confidence", det.get("score", 0))
                                best_conf = best_detection.get("confidence", best_detection.get("score", 0)) if best_detection else 0
                                if best_detection is None or det_conf > best_conf:
                                    best_detection = det
                        
                        if best_detection:
                            # Extract bounding box - try different formats
                            box = best_detection.get("box", best_detection.get("bbox", {}))
                            
                            # Handle different box formats
                            if isinstance(box, dict):
                                x1 = box.get("x1", box.get("xmin", box.get("left", 0)))
                                y1 = box.get("y1", box.get("ymin", box.get("top", 0)))
                                x2 = box.get("x2", box.get("xmax", box.get("right", 1)))
                                y2 = box.get("y2", box.get("ymax", box.get("bottom", 1)))
                            elif isinstance(box, (list, tuple)) and len(box) >= 4:
                                x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
                            else:
                                # Fallback to center
                                x1, y1, x2, y2 = 0.4, 0.4, 0.6, 0.6
                            
                            # Convert coordinates to percentages
                            # If coordinates look like pixels (> 1), normalize by image dimensions
                            if x2 > 1.0:
                                # Pixel coordinates - convert to percentage
                                x1_pct = (x1 / img_width) * 100
                                y1_pct = (y1 / img_height) * 100
                                x2_pct = (x2 / img_width) * 100
                                y2_pct = (y2 / img_height) * 100
                            else:
                                # Already normalized (0-1) - convert to percentage
                                x1_pct = x1 * 100
                                y1_pct = y1 * 100
                                x2_pct = x2 * 100
                                y2_pct = y2 * 100
                            
                            center_x = (x1_pct + x2_pct) / 2
                            center_y = (y1_pct + y2_pct) / 2
                            
                            results.append({
                                "id": query_data.get("id", len(results)),
                                "title": query_data.get("title", "Detail"),
                                "query": query_text,
                                "x": round(center_x, 1),
                                "y": round(center_y, 1),
                                "confidence": round(best_detection.get("confidence", best_detection.get("score", 0)), 3),
                                "box": {
                                    "x1": round(x1_pct, 1),
                                    "y1": round(y1_pct, 1),
                                    "x2": round(x2_pct, 1),
                                    "y2": round(y2_pct, 1)
                                }
                            })
                            continue
                
                # If we reach here, no detection was found
                results.append({
                    "id": query_data.get("id", len(results)),
                    "title": query_data.get("title", "Detail"),
                    "query": query_text,
                    "x": 50.0,
                    "y": 50.0,
                    "confidence": 0.0,
                    "box": None,
                    "error": "No detection found"
                })
                    
            except Exception as e:
                # Error with this query - use center as fallback
                results.append({
                    "id": query_data.get("id", len(results)),
                    "title": query_data.get("title", "Detail"),
                    "query": query_text,
                    "x": 50.0,
                    "y": 50.0,
                    "confidence": 0.0,
                    "box": None,
                    "error": str(e)
                })
        
        return results
    
    def localize_from_xml_details(
        self,
        image_path: str,
        details: List[Dict[str, str]]
    ) -> List[Dict]:
        """
        Convenience method to localize from parsed XML details.
        
        Args:
            image_path: Path to the image
            details: List of detail dicts with 'query' and 'title' keys
            
        Returns:
            List of localization results
        """
        queries = [
            {
                "id": idx,
                "query": detail.get("query", ""),
                "title": detail.get("title", "Detail")
            }
            for idx, detail in enumerate(details)
            if detail.get("query")
        ]
        
        return self.localize_queries(image_path, queries)

