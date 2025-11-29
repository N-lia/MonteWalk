from __future__ import annotations
from typing import Iterable
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes

class ProfessionalTheme(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.blue,
        secondary_hue: colors.Color | str = colors.slate,
        neutral_hue: colors.Color | str = colors.slate,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_sm,
        text_size: sizes.Size | str = sizes.text_md,
        font: fonts.Font | str | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("Inter"),
            "ui-sans-serif",
            "system-ui",
            "sans-serif",
        ),
        font_mono: fonts.Font | str | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("JetBrains Mono"),
            "ui-monospace",
            "Consolas",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )
        
        super().set(
            # Body
            body_background_fill="*neutral_950",
            body_text_color="*neutral_100",
            body_text_color_subdued="*neutral_400",
            
            # Block
            block_background_fill="*neutral_900",
            block_border_color="*neutral_800",
            block_border_width="1px",
            block_info_text_color="*neutral_400",
            block_label_background_fill="*neutral_900",
            block_label_border_color="*neutral_800",
            block_label_border_width="1px",
            block_label_text_color="*neutral_200",
            block_shadow="none",
            block_title_text_color="*neutral_100",
            
            # Button
            button_primary_background_fill="*primary_600",
            button_primary_background_fill_hover="*primary_500",
            button_primary_text_color="white",
            button_primary_border_color="*primary_500",
            button_secondary_background_fill="*neutral_800",
            button_secondary_background_fill_hover="*neutral_700",
            button_secondary_text_color="*neutral_200",
            button_secondary_border_color="*neutral_700",
            
            # Input
            input_background_fill="*neutral_900",
            input_border_color="*neutral_800",
            input_border_color_focus="*primary_500",
            input_placeholder_color="*neutral_500",
            input_shadow="none",
            input_shadow_focus="0 0 0 2px *primary_500",
            
            # Layout
            layout_gap="*spacing_lg",
            
            # Borders
            border_color_primary="*neutral_800",
            
            # Checkbox
            checkbox_background_color="*neutral_800",
            checkbox_border_color="*neutral_700",
            checkbox_label_text_color="*neutral_200",
            
            # Slider
            slider_color="*primary_500",
        )
