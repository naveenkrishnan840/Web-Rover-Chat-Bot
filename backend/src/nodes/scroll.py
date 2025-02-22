from src.graph_state import AgentState


async def scroll_node(state: AgentState):
    page = state["page"]
    action = state["action"]
    scroll_type = action["action"].split(" ")[1].split("[")[1].split("]")[0]
    direction = action["args"]

    async def is_pdf_page():
        current_url = page.url
        return (
                current_url.lower().endswith('.pdf') or
                'pdf' in current_url.lower() or
                '/pdf/' in current_url.lower()
        )

    async def try_scroll_methods(is_down: bool):
        keys = ["PageDown", "Space", "ArrowDown", "j"] if is_down else ["PageUp", "ArrowUp", "k"]
        # Reduced to just one key press for more controlled scrolling
        for key in keys:
            try:
                await page.keyboard.press(key)
                await page.wait_for_timeout(100)
                break  # Exit after first successful key press
            except Exception as e:
                print(f"Failed with key {key}: {str(e)}")
                continue

    if scroll_type == "WINDOW":
        is_pdf = await is_pdf_page()


        if is_pdf:
            try:
                # Wait for PDF to load
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(1000)

                # Try to click on the PDF to ensure focus
                try:
                    await page.mouse.click(300, 300)  # Click somewhere in the middle of the page
                except Exception:
                    pass

                # Single scroll attempt
                await try_scroll_methods(direction.lower() == "down")
                await page.wait_for_timeout(500)

                return {
                    "last_action": f"Scroll : scrolled {direction} on PDF document",
                    "actions_taken": [f"Scroll : scrolled {direction} on PDF document"]
                }

            except Exception as e:
                print(f"PDF scrolling error: {str(e)}")
                return {
                    "action": "retry",
                    "args": f"Error scrolling PDF: {str(e)}",
                    "actions_taken": [f"Error scrolling PDF: {str(e)}"]
                }
        else:
            # Regular webpage scrolling with exactly 500px
            scroll_amount = 500  # Changed from 800 to 500
            scroll_direction = -scroll_amount if direction.lower() == "up" else scroll_amount
            try:
                await page.evaluate(f"""
                    window.scrollBy({{
                        top: {scroll_direction},
                        left: 0,
                        behavior: 'smooth'
                    }});
                """)
            except Exception:
                await page.evaluate(f"window.scrollBy(0, {scroll_direction})")

        await page.wait_for_timeout(500)

        return {
            "last_action": f"Scroll : scrolled {direction}",
            "actions_taken": [f"Scroll : scrolled {direction}"]
        }

    else:
        # Element-specific scrolling
        try:
            bbox_id = int(action["action"].split("[")[1].split("]")[0])
            if bbox_id not in [bbox["id"] for bbox in state["bboxes"]]:
                return {
                    "action": "retry",
                    "args": f"Could not find bbox with id {bbox_id}",
                    "actions_taken": [f"Could not find bbox with id {bbox_id}"]
                }

            bbox = state["bboxes"][bbox_id]
            scroll_amount = 200
            scroll_direction = -scroll_amount if direction.lower() == "up" else scroll_amount

            await page.mouse.move(bbox["x"], bbox["y"])
            await page.mouse.wheel(0, scroll_direction)

            return {
                "last_action": f"Scroll : scrolled {direction} at element {bbox_id}",
                "actions_taken": [f"Scroll : scrolled {direction} at element {bbox_id}"]
            }

        except Exception as e:
            return {
                "action": "retry",
                "args": f"Error scrolling element: {str(e)}",
                "actions_taken": [f"Error scrolling element: {str(e)}"]
            }
