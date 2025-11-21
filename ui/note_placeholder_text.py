example_placeholder_text = """
    <table cellspacing="8" cellpadding="4" align="center">
    <tr>
        <th align="left" style="color:#ccc;">Syntax</th>
        <th align="left" style="color:#ccc;">Preview</th>
    </tr>
    <tr>
        <td><code>**bold**</code></td>
        <td><b>bold</b></td>
    </tr>
    <tr>
        <td><code>_italic_</code></td>
        <td><i>italic</i></td>
    </tr>
    <tr>
        <td><code># Header 1</code></td>
        <td><h3 style="margin:0;">Header 1</h3></td>
    </tr>
    <tr>
        <td><code>## Header 2</code></td>
        <td><h4 style="margin:0;">Header 2</h4></td>
    </tr>
    <tr>
        <td><code>### Header 3</code></td>
        <td><h5 style="margin:0;">Header 3</h5></td>
    </tr>
    <tr>
        <td><code>[title](https://...)</code></td>
        <td><a href="https://example.com" style="color:#5dade2;">title</a></td>
    </tr>
    <tr>
        <td><code>![Image](path/to/image.png)</code></td>
        <td><img src="resources/icons/image_example.png"></td>
    </tr>
    <tr>
        <td><code>```\ncode\n```</code></td>
        <td>
            <pre style="background:#222; color:#0f0; padding:6px; border-radius:4px; margin:0;">
    def hello():
        print("Hello, world!")
            </pre>
        </td>
    </tr>
    <tr>
        <td><code>> quote</code></td>
        <td>
            <blockquote style="border-left:3px solid #888; padding-left:8px; color:#aaa; margin:0;">
    This is a blockquote
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>- item</code></td>
        <td>
            <ul style="margin:0;">
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><code>1. item</code></td>
        <td>
            <ol style="margin:0;">
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ol>
        </td>
    </tr>
    </table>
    """