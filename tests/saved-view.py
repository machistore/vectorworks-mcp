import vs


def collect_view_settings():
    """現在のビュー設定項目を収集してリストで返す
    
    Returns:
        list: 設定項目の文字列リスト
    """
    info_lines = []
    info_lines.append("=== Vectorworks View Settings ===\n")
    
    # Document name
    try:
        doc_name = vs.GetDocumentName()
        info_lines.append(f"Document: {doc_name}")
    except Exception as e:
        info_lines.append(f"Document: Error ({e})")
    
    # 3D View info
    try:
        x_angle, y_angle, z_angle, offset = vs.GetView()
        info_lines.append(f"X Angle: {x_angle:.2f}")
        info_lines.append(f"Y Angle: {y_angle:.2f}")
        info_lines.append(f"Z Angle: {z_angle:.2f}")
        info_lines.append(f"View Center: {offset}")
    except Exception as e:
        info_lines.append(f"3D View: Error ({e})")
    
    # Zoom info
    try:
        zoom = vs.GetZoom()
        info_lines.append(f"Zoom: {zoom:.1f}%")
    except Exception as e:
        info_lines.append(f"Zoom: Error ({e})")
    
    # Layer info
    try:
        active_layer = vs.ActLayer()
        if active_layer:
            layer_name = vs.GetLName(active_layer)
            info_lines.append(f"Active Layer: {layer_name}")
            layer_vis = vs.GetLVis(active_layer)
            info_lines.append(f"Layer Visibility: {layer_vis}")
        else:
            info_lines.append("Active Layer: None")
    except Exception as e:
        info_lines.append(f"Layer Info: Error ({e})")
    
    # Class info
    try:
        active_class = vs.ActiveClass()
        info_lines.append(f"Active Class: {active_class}")
        if active_class:
            class_vis = vs.GetCVis(active_class)
            info_lines.append(f"Class Visibility: {class_vis}")
    except Exception as e:
        info_lines.append(f"Class Info: Error ({e})")
    
    # Version info
    try:
        version = vs.GetVersion()
        info_lines.append(f"Vectorworks Version: {version}")
    except Exception as e:
        info_lines.append(f"Version: Error ({e})")
    
    # Additional layer info
    try:
        layer_options = vs.GetLayerOptions()
        info_lines.append(f"Layer Options: {layer_options}")
    except Exception as e:
        info_lines.append(f"Layer Options: Error ({e})")
    
    # Projection info
    try:
        active_layer = vs.ActLayer()
        if active_layer:
            projection = vs.GetProjection(active_layer)
            info_lines.append(f"Projection: {projection}")
    except Exception as e:
        info_lines.append(f"Projection: Error ({e})")
    
    # Drawing size
    try:
        drawing_size = vs.GetDrawingSizeRect()
        info_lines.append(f"Drawing Size: {drawing_size}")
    except Exception as e:
        info_lines.append(f"Drawing Size: Error ({e})")
    
    # Working plane
    try:
        working_plane = vs.GetWorkingPlane()
        info_lines.append(f"Working Plane: {working_plane}")
    except Exception as e:
        info_lines.append(f"Working Plane: Error ({e})")
    
    return info_lines


def display_settings_dialog(info_lines):
    """設定項目リストをダイアログで表示する
    
    Args:
        info_lines (list): 設定項目の文字列リスト
    """
    # Display in dialog
    message = "\n".join(info_lines)
    
    # Split message if too long
    max_length = 2000
    if len(message) <= max_length:
        vs.AlrtDialog(message)
    else:
        # Split into parts
        parts = []
        current_part = []
        current_length = 0
        
        for line in info_lines:
            if current_length + len(line) + 1 > max_length:
                parts.append("\n".join(current_part))
                current_part = [line]
                current_length = len(line)
            else:
                current_part.append(line)
                current_length += len(line) + 1
        
        if current_part:
            parts.append("\n".join(current_part))
        
        # Display each part
        for i, part in enumerate(parts):
            title = f"Vectorworks Settings {i+1}/{len(parts)}\n\n"
            vs.AlrtDialog(title + part)


def main():
    """メイン実行関数"""
    try:
        # データを収集
        settings_data = collect_view_settings()
        # ダイアログで表示
        display_settings_dialog(settings_data)
    except Exception as e:
        vs.AlrtDialog(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
