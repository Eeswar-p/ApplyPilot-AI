from typing import List, Dict, Any, Optional
from playwright.sync_api import Page, Locator

class FormFieldDescriptor:
    """Represents a scanned form input field."""

    def __init__(
        self,
        field_id: str,
        name: str,
        field_type: str,
        label: str,
        required: bool = False,
        options: Optional[List[str]] = None,
        selector: str = "",
        current_value: str = ""
    ):
        self.field_id = field_id
        self.name = name
        self.field_type = field_type
        self.label = label
        self.required = required
        self.options = options or []
        self.selector = selector
        self.current_value = current_value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.field_id,
            "name": self.name,
            "type": self.field_type,
            "label": self.label,
            "required": self.required,
            "options": self.options,
            "selector": self.selector,
            "current_value": self.current_value,
        }

class FormScanner:
    """Scans DOM for form fields and accurately extracts field labels, types, and constraints."""

    def __init__(self, page: Page):
        self.page = page

    def _resolve_label(self, element: Locator) -> str:
        """Resolve readable label using aria-label, <label for>, placeholder, or element name."""
        try:
            # 1. Check aria-label
            aria_label = element.get_attribute("aria-label")
            if aria_label and aria_label.strip():
                return aria_label.strip()

            # 2. Check label[for="id"]
            elem_id = element.get_attribute("id")
            if elem_id:
                label_loc = self.page.locator(f"label[for='{elem_id}']")
                if label_loc.count() > 0:
                    text = label_loc.first.inner_text().strip()
                    if text:
                        return text

            # 3. Check placeholder
            placeholder = element.get_attribute("placeholder")
            if placeholder and placeholder.strip():
                return placeholder.strip()

            # 4. Check name attribute
            name = element.get_attribute("name")
            if name:
                clean_name = name.replace("_", " ").replace("-", " ").title()
                return clean_name

        except Exception:
            pass

        return "Unlabeled Field"

    def scan_form_fields(self, root_selector: str = "body") -> List[FormFieldDescriptor]:
        """Scan page or container for interactive application inputs."""
        fields: List[FormFieldDescriptor] = []
        ignored_types = {"hidden", "submit", "button", "reset", "image"}

        # Scan <input>, <select>, <textarea>
        query = f"{root_selector} input, {root_selector} select, {root_selector} textarea"
        elements = self.page.locator(query)
        count = elements.count()

        for idx in range(count):
            try:
                el = elements.nth(idx)
                tag_name = el.evaluate("el => el.tagName.toLowerCase()")
                input_type = el.get_attribute("type") or "text" if tag_name == "input" else tag_name

                if input_type in ignored_types:
                    continue

                elem_id = el.get_attribute("id") or f"field_{idx}"
                name = el.get_attribute("name") or elem_id
                required = el.get_attribute("required") is not None or el.get_attribute("aria-required") == "true"
                label = self._resolve_label(el)
                current_value = el.input_value() if tag_name in ("input", "textarea") else ""

                options = []
                if tag_name == "select":
                    options = el.locator("option").all_inner_texts()
                    options = [o.strip() for o in options if o.strip()]

                field_desc = FormFieldDescriptor(
                    field_id=elem_id,
                    name=name,
                    field_type=input_type,
                    label=label,
                    required=required,
                    options=options,
                    selector=f"#{elem_id}" if elem_id and not elem_id.startswith("field_") else f"{tag_name}[name='{name}']",
                    current_value=current_value,
                )
                fields.append(field_desc)

            except Exception:
                continue

        return fields
