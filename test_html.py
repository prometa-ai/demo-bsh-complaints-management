import re
from bs4 import BeautifulSoup

def validate_css_styles():
    """Validate the CSS styling in the HTML templates."""
    print("Validating CSS styles in the templates...")
    
    # Read the unified_complaint.html file
    with open('templates/unified_complaint.html', 'r') as file:
        html_content = file.read()
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all style attributes
    elements_with_style = soup.find_all(attrs={"style": True})
    
    print(f"Found {len(elements_with_style)} elements with style attributes")
    
    # Regex pattern for valid CSS declaration
    css_pattern = re.compile(r'^\s*([a-zA-Z-]+)\s*:\s*([^;]+)(?:;|$)')
    
    # Check each style attribute
    valid_count = 0
    for element in elements_with_style:
        style_attr = element['style']
        print(f"\nChecking: {style_attr}")
        
        # Split the style attribute by semicolons
        declarations = style_attr.split(';')
        
        all_valid = True
        for declaration in declarations:
            declaration = declaration.strip()
            if not declaration:  # Skip empty declarations
                continue
                
            match = css_pattern.match(declaration)
            if not match:
                print(f"  Invalid CSS declaration: '{declaration}'")
                all_valid = False
            else:
                property_name = match.group(1)
                property_value = match.group(2)
                print(f"  Valid CSS: {property_name}: {property_value}")
        
        if all_valid:
            valid_count += 1
    
    print(f"\nValidation complete: {valid_count}/{len(elements_with_style)} elements have valid CSS styling")

if __name__ == "__main__":
    validate_css_styles() 