from manim import *
import os

class FinalResearchStory(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a0a0a"
        
        # =============== 1. 开场：问题与挑战 ===============
        title = Text("连续2004个数中恰有12个质数", font_size=48, color=BLUE)
        subtitle = Text("一项计算数论的探索与突破", font_size=36, color=GRAY_A)
        subtitle.next_to(title, DOWN)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle))
        self.wait(1)

        
        # Problem equation with box
        problem_tex = MathTex(r"\pi(N+2003) - \pi(N-1) = 12", font_size=40)
        problem_box = SurroundingRectangle(
            problem_tex,
            color=BLUE_D,
            buff=0.3,
            corner_radius=0.1
        )
        
        problem_group = VGroup(problem_box, problem_tex).next_to(subtitle, DOWN, buff=1)
        
        self.play(
            Write(problem_tex),
            Create(problem_box),
            run_time=1.5
        )
        self.wait(0.5)

        # "惜败" with animation
        sad = Text("✓ 验证至 105.93B：无解", color=RED, font_size=32)
        sad.next_to(problem_group, DOWN, buff=0.8)
        
        # Add a faded background
        sad_bg = Rectangle(
            width=sad.width + 1,
            height=sad.height + 0.5,
            fill_color=RED_D,
            fill_opacity=0.2,
            stroke_width=0
        ).move_to(sad)
        
        self.play(
            FadeIn(sad_bg, scale=0.5),
            Write(sad),
            run_time=1
        )
        self.wait(2)

        # =============== 2. 理论转折：CRT构造 ===============
        self.play(
            *[FadeOut(mob, shift=DOWN) for mob in [title, subtitle, problem_group, sad_bg, sad]]
        )

        # CRT section with bullet points
        crt_title = Text("数学突破：中国剩余定理构造", font_size=44, color=TEAL)
        crt_title.to_edge(UP, buff=1)
        
        # Add underline
        underline = Line(
            LEFT * (crt_title.width/2 + 0.5),
            RIGHT * (crt_title.width/2 + 0.5),
            color=TEAL
        ).next_to(crt_title, DOWN, buff=0.2)
        
        self.play(
            Write(crt_title),
            GrowFromCenter(underline)
        )
        self.wait(0.5)

        # CRT explanation with bullet points
        bullet_points = VGroup(
            Text("• 利用模数约束质数位置", color=GREEN),
            Text("• 构造允许模式H：12个可接受位置", color=YELLOW),
            Text("• 理论预测：解的存在区域", color=BLUE)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        bullet_points.next_to(underline, DOWN, buff=0.8)
        
        for point in bullet_points:
            self.play(Write(point), run_time=0.8)
            self.wait(0.3)

        # H pattern with highlight
        H_text = MathTex(
            r"H = [166, 278, 604, 724, 1096, 1256,",
            r"1306, 1492, 1514, 1564, 1574, 1712]",
            font_size=28
        ).next_to(bullet_points, DOWN, buff=0.8)
        
        # Color the numbers
        H_text[0][1:].set_color_by_gradient(ORANGE, GOLD)
        H_text[1][:-1].set_color_by_gradient(GOLD, ORANGE)
        
        # Add braces to show count
        brace = Brace(H_text, DOWN, color=GRAY)
        brace_text = Text("12个位置", color=GRAY, font_size=24)
        brace_text.next_to(brace, DOWN, buff=0.1)
        
        self.play(Write(H_text))
        self.play(GrowFromCenter(brace), Write(brace_text))
        self.wait(2)

        # =============== 3. 奇迹命中：首个解 ===============
        self.play(
            *[FadeOut(mob) for mob in [crt_title, underline, bullet_points, H_text, brace, brace_text]]
        )

        # Dramatic reveal of the hit
        hit_bg = Rectangle(
            width=config.frame_width,
            height=1.5,
            fill_color=YELLOW,
            fill_opacity=0.2,
            stroke_width=0
        )
        
        hit = Text("第10次尝试：命中！", font_size=52, color=YELLOW)
        
        self.play(
            FadeIn(hit_bg, scale=2),
            Write(hit, run_time=1.5)
        )
        self.wait(1)

        # Reveal N0 with highlighting
        N0 = MathTex(
            r"N_0 = 28365\ldots 1785\ \text{(72 digits)}",
            font_size=36,
            color=GOLD
        ).next_to(hit, DOWN, buff=1)
        
        # Create zoom effect on the number
        self.play(
            Write(N0),
            hit_bg.animate.set_height(2.5),
            run_time=1.5
        )
        
        # Highlight digits
        self.play(
            N0[0][0:4].animate.set_color(GREEN),  # 28365
            N0[0][-4:-1].animate.set_color(BLUE),  # 1785
            run_time=1
        )
        self.wait(2)

        # =============== 4. 大规模验证：5691个解 ===============
        self.play(FadeOut(hit_bg), FadeOut(hit), FadeOut(N0))

        # Title for data section
        data_title = Text("大规模计算验证", font_size=40, color=PURPLE)
        data_title.to_edge(UP)
        self.play(Write(data_title))
        
        # Counter animation for 5691
        counter = Integer(0, font_size=72, color=GREEN)
        counter.next_to(data_title, DOWN, buff=1)
        
        self.play(Write(counter))
        self.play(
            counter.animate.set_value(5691),
            run_time=2,
            rate_func=linear
        )
        
        counter_text = Text("个解被成功验证", font_size=36, color=WHITE).next_to(counter, RIGHT)
        self.play(Write(counter_text))
        self.wait(1)

        # Image gallery with improved transitions
        scale = 0.55
        
        # Image 1: Density plot
        self.play(FadeOut(counter), FadeOut(counter_text))
        
        img1 = ImageMobject("solutions_density.png").scale(scale)
        img1.next_to(data_title, DOWN, buff=1)
        
        caption1 = Text("图1：5691个解的空间分布（围绕 N₀）", font_size=24, color=GRAY_A)
        caption1.next_to(img1, DOWN)
        
        # Add frame around image
        frame1 = SurroundingRectangle(img1, color=BLUE_D, buff=0.1, corner_radius=0.05)
        
        self.play(
            FadeIn(img1),
            Create(frame1),
            Write(caption1),
            run_time=1.5
        )
        
        # Annotations on image
        arrow1 = Arrow(
            LEFT * 2 + UP,
            ORIGIN,
            color=RED
        ).next_to(img1, LEFT, buff=0.5)
        
        arrow_text1 = Text("峰值密度", font_size=20, color=RED).next_to(arrow1, LEFT)
        
        self.play(GrowArrow(arrow1), Write(arrow_text1))
        self.wait(2)
        
        self.play(FadeOut(arrow1), FadeOut(arrow_text1))
        self.wait(1)

        # Transition to next image
        self.play(
            img1.animate.shift(LEFT * 7),
            frame1.animate.shift(LEFT * 7),
            caption1.animate.shift(LEFT * 7),
            run_time=1.5
        )

        # Image 2: Cumulative plot
        img2 = ImageMobject("solutions_cumulative.png").scale(scale)
        img2.move_to(ORIGIN)
        
        caption2 = Text("图2：累积解数量 vs 理论均匀分布", font_size=24, color=GRAY_A)
        caption2.next_to(img2, DOWN)
        
        frame2 = SurroundingRectangle(img2, color=GREEN_D, buff=0.1, corner_radius=0.05)
        
        self.play(
            FadeIn(img2),
            Create(frame2),
            Write(caption2),
            run_time=1.5
        )
        
        # Add comparison dots
        dot_actual = Dot(LEFT * 2 + UP * 1.5, color=GREEN)
        dot_theory = Dot(LEFT * 1 + DOWN * 0.5, color=RED)
        
        actual_label = Text("实际", font_size=18, color=GREEN).next_to(dot_actual, UP)
        theory_label = Text("理论", font_size=18, color=RED).next_to(dot_theory, DOWN)
        
        self.play(
            FadeIn(dot_actual, scale=0),
            FadeIn(dot_theory, scale=0),
            Write(actual_label),
            Write(theory_label)
        )
        self.wait(2)
        
        self.play(
            *[FadeOut(mob) for mob in [dot_actual, dot_theory, actual_label, theory_label]]
        )
        self.wait(1)

        # Image 3: Analysis summary
        self.play(
            img2.animate.shift(RIGHT * 7),
            frame2.animate.shift(RIGHT * 7),
            caption2.animate.shift(RIGHT * 7),
            run_time=1.5
        )
        
        img3 = ImageMobject("solutions_analysis.png").scale(scale)
        img3.move_to(ORIGIN)
        
        caption3 = Text("图3：综合统计分析", font_size=24, color=GRAY_A)
        caption3.next_to(img3, DOWN)
        
        frame3 = SurroundingRectangle(img3, color=ORANGE, buff=0.1, corner_radius=0.05)
        
        self.play(
            FadeIn(img3),
            Create(frame3),
            Write(caption3),
            run_time=1.5
        )
        
        # Add statistical highlights
        stats = VGroup(
            Text("KDE峰值密度: 5.0e-10", font_size=20, color=GREEN),
            Text("平均间隙: 3.51×10⁴", font_size=20, color=BLUE),
            Text("中位间隙: 2.84×10⁴", font_size=20, color=PURPLE)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        stats.to_corner(UR, buff=1)
        
        for stat in stats:
            self.play(Write(stat), run_time=0.5)
        
        self.wait(3)

        # =============== 5. 结尾：意义升华 ===============
        self.play(
            *[FadeOut(mob) for mob in [
                img1, img2, img3,
                frame1, frame2, frame3,
                caption1, caption2, caption3,
                stats, data_title
            ]]
        )

        # Final message with elegant animation
        conclusion_1 = Text("从 105.93B 的‘惜败’", font_size=44, color=RED)
        conclusion_2 = Text("到 5691 个解的‘解岛’发现", font_size=44, color=GREEN)
        conclusion_3 = Text("——数学引导 + 计算勇气 =", font_size=36, color=WHITE)
        conclusion_4 = Text("不可能变为可能", font_size=48, color=YELLOW)
        
        conclusion_group = VGroup(
            conclusion_1, conclusion_2, conclusion_3, conclusion_4
        ).arrange(DOWN, buff=0.6)
        conclusion_group.center()
        
        # Animate with pause between each line
        self.play(Write(conclusion_1))
        self.wait(1)
        
        self.play(Write(conclusion_2))
        self.wait(1)
        
        self.play(Write(conclusion_3))
        self.wait(1)
        
        # Highlight the final message
        self.play(
            Write(conclusion_4),
            conclusion_4.animate.scale(1.2),
            run_time=2
        )
        self.wait(2)

        # Add sparkle effect around final message
        sparkles = VGroup(*[
            Dot(
                conclusion_4.get_center() + np.array([x, y, 0]),
                color=YELLOW,
                radius=0.05
            )
            for x, y in [(0.5, 0.5), (-0.5, 0.3), (0.3, -0.5), (-0.4, -0.4)]
        ])
        
        self.play(
            *[GrowFromCenter(sparkle) for sparkle in sparkles],
            run_time=0.5
        )
        self.wait(2)

        # Final attribution
        credit = Text(
            "数据来源：局部搜索 + gmpy2 验证 | 可视化：Manim + Matplotlib",
            font_size=20,
            color=GRAY
        )
        credit.to_edge(DOWN, buff=0.5)
        
        self.play(FadeIn(credit, shift=UP))
        self.wait(3)
        
        # Fade out everything
        self.play(
            *[FadeOut(mob, shift=UP) for mob in [conclusion_group, credit, sparkles]],
            run_time=2
        )