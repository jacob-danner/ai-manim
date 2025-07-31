'''
Description:
The image displays a diagram titled "Initial Residual Streams" in a sans-serif font at the top left.

On the left side of the diagram, vertically aligned text reads "He", "llo", "Wo", and "rld", with each word slightly indented to the right and below the previous one, creating a staggered effect.

To the right of this text, there are three large, rectangular blocks stacked behind each other, creating a sense of depth. Each block is divided into smaller, equal-sized rectangular segments by vertical lines.
The front-most block is white with black outlines, and it is the largest, extending downwards. It is divided into 8 vertical segments.
Behind it, slightly offset to the top and left, is a green block. This green block is also divided into 8 vertical segments, but only the top 4 segments are filled with green color, while the bottom part is white with black outlines.
Behind the green block, and again slightly offset to the top and left, is a purple block. This purple block is also divided into 8 vertical segments, but only the top 4 segments are filled with purple color, while the bottom part is white with black outlines.

On the right side of the diagram, there is text indicating dimensions:
"batch tokens dimension"
"1 4 8"
This text is aligned in columns, with "1" under "batch", "4" under "tokens", and "8" under "dimension".

The overall background of the diagram is white.
'''

from manim import *

class InitialResidualStreams(Scene):
    def construct(self):
        # Set the background color to white
        self.camera.background_color = WHITE

        # 1. Title
        title = Text("Initial Residual Streams", font_size=36, font="sans-serif", color=BLACK).to_corner(UL)
        self.add(title)

        # 2. Staggered Text
        words = ["He", "llo", "Wo", "rld"]
        staggered_text_group = VGroup()
        
        # Create and position the first word
        first_word = Text(words[0], font_size=30, color=BLACK)
        staggered_text_group.add(first_word)

        # Create and position subsequent words with a staggered effect
        for i in range(1, len(words)):
            next_word = Text(words[i], font_size=30, color=BLACK)
            # Position below the previous word and slightly to the right
            next_word.next_to(staggered_text_group[-1], DOWN, buff=0.2)
            next_word.shift(RIGHT * 0.5) 
            staggered_text_group.add(next_word)
        
        # Position the entire staggered text group on the left side
        staggered_text_group.to_edge(LEFT).shift(RIGHT * 1.5 + UP * 0.5)
        self.add(staggered_text_group)

        # 3. Stacked Rectangular Blocks
        block_width = 1.5
        block_height = 6.0
        segment_height = block_height / 8

        # Helper function to create a segmented block
        # color_segments: list of colors for each of the 8 segments. 
        #                 Use None or WHITE for segments that should be white with black outline.
        def create_segmented_block(color_segments, outline_color=BLACK, fill_opacity=1.0):
            segments = VGroup()
            for i in range(8):
                segment_rect = Rectangle(
                    width=block_width,
                    height=segment_height,
                    stroke_color=outline_color,
                    fill_opacity=fill_opacity
                )
                # Set fill color based on the provided list, defaulting to white if None
                if i < len(color_segments) and color_segments[i] is not None:
                    segment_rect.set_fill(color_segments[i], opacity=fill_opacity)
                else:
                    segment_rect.set_fill(WHITE, opacity=fill_opacity) 
                segments.add(segment_rect)
            
            # Arrange segments vertically from top to bottom without any buffer
            segments.arrange(DOWN, buff=0)
            return segments

        # White Block (Front-most)
        white_block_colors = [WHITE] * 8 # All segments are white
        white_block = create_segmented_block(white_block_colors)
        white_block.move_to(ORIGIN).shift(RIGHT * 2) # Position it to the right of center
        white_block.set_z_index(2) # Highest z-index for front-most appearance

        # Green Block (Middle)
        green_block_colors = [GREEN_B] * 4 + [None] * 4 # Top 4 green, bottom 4 white
        green_block = create_segmented_block(green_block_colors)
        # Position slightly up and left relative to the white block for depth effect
        green_block.next_to(white_block, UP + LEFT, buff=0) # Start close
        green_block.shift(UP * 0.3 + LEFT * 0.3) # Manual offset for visual depth
        green_block.set_z_index(1) # Middle z-index

        # Purple Block (Back-most)
        purple_block_colors = [PURPLE_B] * 4 + [None] * 4 # Top 4 purple, bottom 4 white
        purple_block = create_segmented_block(purple_block_colors)
        # Position slightly up and left relative to the green block for further depth
        purple_block.next_to(green_block, UP + LEFT, buff=0) # Start close
        purple_block.shift(UP * 0.3 + LEFT * 0.3) # Manual offset for visual depth
        purple_block.set_z_index(0) # Lowest z-index

        # Add blocks to the scene in order from back to front for correct layering
        self.add(purple_block, green_block, white_block)

        # 4. Dimension Text
        # Create individual text objects for precise alignment
        batch_label = Text("batch", font_size=24, color=BLACK)
        tokens_label = Text("tokens", font_size=24, color=BLACK)
        dimension_label = Text("dimension", font_size=24, color=BLACK)

        batch_value = Text("1", font_size=24, color=BLACK)
        tokens_value = Text("4", font_size=24, color=BLACK)
        dimension_value = Text("8", font_size=24, color=BLACK)

        # Arrange the labels horizontally
        top_row_labels = VGroup(batch_label, tokens_label, dimension_label).arrange(RIGHT, buff=1.0)
        
        # Arrange the values horizontally
        bottom_row_values = VGroup(batch_value, tokens_value, dimension_value).arrange(RIGHT, buff=1.0)
        
        # Align the values directly under their corresponding labels
        bottom_row_values[0].align_to(top_row_labels[0], LEFT)
        bottom_row_values[1].align_to(top_row_labels[1], LEFT)
        bottom_row_values[2].align_to(top_row_labels[2], LEFT)

        # Group the two rows and arrange them vertically
        dimension_group = VGroup(top_row_labels, bottom_row_values).arrange(DOWN, buff=0.5)
        
        # Position the entire dimension group on the right side of the scene
        dimension_group.to_edge(RIGHT).shift(LEFT * 1.5 + UP * 1.5)
        self.add(dimension_group)