from videodb.editor import (
    Timeline,
    Track,
    Clip,
    VideoAsset,
    TextAsset,
    Fit,
    Position,
    Offset,
    Font,
    Background,
    TextAlignment,
    Border,
    Shadow,
    Transition,
)


def build_timeline(conn, video_id: str, total_duration: float, scenes: list[dict]) -> str:
    timeline = Timeline(conn)
    timeline.resolution = "1920x1080"
    timeline.background = "#000000"

    video_track = Track()
    video_track.add_clip(
        0,
        Clip(
            asset=VideoAsset(id=video_id, volume=1.0),
            duration=total_duration,
            fit=Fit.contain,
        ),
    )

    text_track = Track()
    for scene in scenes:
        start = scene["start"]
        duration = scene["duration"]
        overlay = scene["overlay_text"]

        text_track.add_clip(
            start,
            Clip(
                asset=TextAsset(
                    text=overlay,
                    font=Font(family="Clear Sans", size=32, color="#FFFFFF", opacity=1.0),
                    background=Background(
                        width=1700,
                        height=90,
                        color="#0EA5E9",
                        opacity=0.85,
                        text_alignment=TextAlignment.center,
                    ),
                    border=Border(color="#38BDF8", width=2.0),
                    shadow=Shadow(color="#000000", x=0, y=2),
                ),
                duration=duration,
                position=Position.bottom_center,
                offset=Offset(x=0, y=-0.06),
                transition=Transition(in_="fade", out="fade", duration=0.3),
            ),
        )

    timeline.add_track(video_track)
    timeline.add_track(text_track)

    stream_url = timeline.generate_stream()
    return stream_url
