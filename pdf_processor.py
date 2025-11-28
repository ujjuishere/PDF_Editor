import fitz  # PyMuPDF
import io

def process_pdf_stream(input_stream):
    """
    Takes a PDF file stream (bytes), processes it, 
    and returns the processed PDF as a bytes object.
    """
    try:
        # Open source PDF from memory stream
        # input_stream.read() gets the bytes from the uploaded file
        doc = fitz.open(stream=input_stream.read(), filetype="pdf")
        
        # Safety check: ensure file is not empty
        if len(doc) == 0:
            return None
            
        page = doc[0]
        width = page.rect.width

        # --- 1. FIND END POINT ---
        end_marker = "TRANSFORM YOUR BODY"
        end_results = page.search_for(end_marker)
        
        if end_results:
            absolute_end_y = end_results[0].y0 - 25
        else:
            absolute_end_y = page.rect.height

        # --- 2. FIND SPLIT POINTS ---
        split_points = [0.0]
        keywords = [
            "Body Composition",
            "Fat Analysis",
            "Metabolic Indicators",
            "Personalized Recommendations"
        ]

        found_y_coords = []
        for key in keywords:
            results = page.search_for(key)
            for match in results:
                # Ignore top summary (y < 600) and ignore content after end point
                if match.y0 > 600 and match.y0 < absolute_end_y:
                    cut_y = match.y0 - 20
                    found_y_coords.append(cut_y)
                    break 
        
        split_points.extend(found_y_coords)
        split_points.append(absolute_end_y)
        split_points.sort()

        # Clean points (min distance 50px)
        clean_split_points = [split_points[0]]
        for i in range(1, len(split_points)):
            if split_points[i] - clean_split_points[-1] > 50:
                clean_split_points.append(split_points[i])
        split_points = clean_split_points

        # --- 3. GENERATE PAGES ---
        out_doc = fitz.open()

        for i in range(len(split_points) - 1):
            y_start = split_points[i]
            y_end = split_points[i+1]
            clip_rect = fitz.Rect(0, y_start, width, y_end)
            
            if clip_rect.height <= 1: continue

            # LAYOUT SETTINGS
            header_height = 0 
            
            # Create Page
            new_page_height = clip_rect.height + header_height
            new_page = out_doc.new_page(width=width, height=new_page_height)

            # --- 1. PLACE CONTENT ---
            new_page.show_pdf_page(
                fitz.Rect(0, header_height, width, new_page_height),
                doc, 
                0, 
                clip=clip_rect
            )

            # --- 2. PAGE 1 BRANDING ---
            if i == 0:
                # A. Base Mask (White)
                mask_y_start = 0
                mask_y_end = 135 
                new_page.draw_rect(
                    fitz.Rect(0, mask_y_start, width, mask_y_end), 
                    color=(1, 1, 1), 
                    fill=(1, 1, 1)
                )

                # B. Dark Banner Background
                banner_height = 90
                banner_y_end = mask_y_start + banner_height
                new_page.draw_rect(
                    fitz.Rect(0, mask_y_start, width, banner_y_end),
                    color=(0.1, 0.1, 0.15),  # Dark Slate/Charcoal
                    fill=(0.1, 0.1, 0.15)
                )

                # C. Orange Accent Line
                new_page.draw_rect(
                    fitz.Rect(0, banner_y_end, width, banner_y_end + 4),
                    color=(1, 0.6, 0),     # Fitness Orange/Gold
                    fill=(1, 0.6, 0)
                )

                # D. Add Styled Text
                text_title = "M&Y Fitness Club"
                text_subtitle = "PERSONAL INFORMATION SUMMARY"
                
                # Dynamic Center Calculation
                title_width = fitz.get_text_length(text_title, fontname="Helvetica-Bold", fontsize=28)
                subtitle_width = fitz.get_text_length(text_subtitle, fontname="Helvetica", fontsize=12)
                
                title_x = (width - title_width) / 2
                subtitle_x = (width - subtitle_width) / 2

                # Insert Title (White)
                new_page.insert_text(
                    (title_x, mask_y_start + 45), 
                    text_title, 
                    fontsize=28, 
                    color=(1, 1, 1),
                    fontname="Helvetica-Bold"
                )

                # Insert Subtitle (Light Grey)
                new_page.insert_text(
                    (subtitle_x, mask_y_start + 70), 
                    text_subtitle, 
                    fontsize=12, 
                    color=(0.9, 0.9, 0.9),
                    fontname="Helvetica"
                )
            
            

        # Save to memory buffer instead of file
        out_buffer = io.BytesIO()
        out_doc.save(out_buffer)
        out_buffer.seek(0)
        return out_buffer.getvalue()

    except Exception as e:
        print(f"Error processing stream: {e}")
        return None