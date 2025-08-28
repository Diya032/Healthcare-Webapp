def prepare_overlay_json(document_id: int, raw_result: list, file_sas_url: str) -> dict:
    if not raw_result:
        return {
            "document_id": document_id,
            "status": "processing",
            "file_url": file_sas_url,
            "annotations": []
        }

    annotations = []

    for page in raw_result:
        page_number = page.get("page_number", 1)
        page_width = page.get("width", 1)
        page_height = page.get("height", 1)
        
        for line in page.get("lines", []):
            text = line.get("content", "")
            polygon = line.get("polygon", [])

            # normalize coordinates 0-1
            normalized = [[pt["x"]/page_width, pt["y"]/page_height] for pt in polygon]
            
            annotations.append({
                "text": text,
                "page": page_number,
                "bounding_box": normalized,
                "label": "text"  # you can map categories later
            })

    return {
        "document_id": document_id,
        "status": "completed",
        "file_url": file_sas_url,
        "annotations": annotations
    }
