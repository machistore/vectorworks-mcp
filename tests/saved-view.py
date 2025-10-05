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
    
    # 全デザインレイヤー情報
    info_lines.append("\n【全デザインレイヤー】")
    try:
        all_layers = get_all_design_layers()
        if all_layers:
            for layer_info in all_layers:
                info_lines.append(f"  {layer_info}")
        else:
            info_lines.append("  デザインレイヤーなし")
    except Exception as e:
        info_lines.append(f"全レイヤー情報: 取得エラー ({e})")
    
    return info_lines


def get_all_design_layers():
    """全てのデザインレイヤー名とその表示状態を取得する
    
    Returns:
        list: [レイヤー名, 表示状態]のペアのリスト
    """
    layer_info_list = []
    
    try:
        # 最初のレイヤーを取得
        current_layer = vs.FLayer()
        
        while current_layer:
            try:
                # レイヤー名を取得
                layer_name = vs.GetLName(current_layer)
                
                # レイヤーの表示状態を取得
                layer_vis = vs.GetLVis(current_layer)
                
                # 表示状態を文字列に変換
                vis_status_map = {
                    0: "通常",      # Normal/Visible
                    2: "グレー",    # Grayed
                    -1: "非表示"    # Invisible
                }
                vis_status = vis_status_map.get(layer_vis, f"不明({layer_vis})")
                
                # [レイヤー名: 表示状態] の形式で追加
                layer_info = f"{layer_name}: {vis_status}"
                layer_info_list.append(layer_info)
                
            except Exception as e:
                # 個別のレイヤー処理でエラーが発生した場合
                layer_info_list.append(f"エラーレイヤー: 取得失敗 ({e})")
            
            # 次のレイヤーに移動
            current_layer = vs.NextLayer(current_layer)
            
    except Exception as e:
        layer_info_list.append(f"レイヤー取得エラー: {e}")
    
    return layer_info_list


def display_settings_dialog(info_lines):
    """設定項目リストを2つのダイアログに分けて表示する
    
    Args:
        info_lines (list): 設定項目の文字列リスト
    """
    # メイン設定情報と全デザインレイヤー情報を分離
    main_settings = []
    layer_settings = []
    
    in_layer_section = False
    
    for line in info_lines:
        if "【全デザインレイヤー】" in line:
            in_layer_section = True
            layer_settings.append(line)
        elif in_layer_section:
            layer_settings.append(line)
        else:
            main_settings.append(line)
    
    # 1回目: メイン設定情報を表示
    if main_settings:
        main_message = "\n".join(main_settings)
        vs.AlrtDialog(main_message)
    
    # 2回目: 全デザインレイヤー情報を表示
    if layer_settings:
        layer_message = "\n".join(layer_settings)
        vs.AlrtDialog(layer_message)


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
