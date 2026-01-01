# Global context menu styles
menu_style = """
/* Top-level menu bar item when selected/hovered */
QMenuBar::item:selected {
    background-color: #000000;  
    color: #FFFFFF;            
}

/* Dropdown menu */
QMenu {
    background-color: #000000;  
    border: 1px solid #303060;  
    border-radius: 4px;         
    padding: 4px;
}

/* Individual menu items */
QMenu::item {
    min-height: 28px;
    padding: 6px 12px;          
    color: #FFFFFF;             
    border-radius: 4px;         
}

/* Hover or keyboard selection */
QMenu::item:selected,
QMenu::item:hover {
    background: #2F3B47;  
    color: #FFFFFF;             
}
"""