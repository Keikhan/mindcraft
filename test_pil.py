try:
    from PIL import Image
    print("PIL is installed and working!")
    
    # Create a test image
    img = Image.new('RGB', (60, 30), color = (73, 109, 137))
    img.save('test_image.png')
    print("Test image created successfully!")
except ImportError as e:
    print(f"Error importing PIL: {e}")
except Exception as e:
    print(f"Unexpected error: {e}") 