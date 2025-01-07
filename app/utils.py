import base64
import datetime
import os

import numpy as np
from dateutil import parser as date_parser
from fastapi import HTTPException, status
from nacl.public import Box, PrivateKey, PublicKey

MOTIVATIONAL_NOTES: list[str] = [
    "Keep up the amazing work, and don’t forget—every submission is a step toward your goals! 🎯✨",
    "You're building something great, one step at a time. Keep pushing forward! 🚀",
    "Every bit of progress counts—you're doing amazing! Keep going! 🌟",
    "Success is built on effort, and you're putting in the work! Fantastic job! 🏆",
    "You're unstoppable! Keep making strides toward your dreams! 🌠",
    "Challenges are stepping stones—you're on the right path! 🌈",
    "Believe in yourself! Every submission is proof of your dedication. 💪",
    "You’ve got what it takes to succeed—keep shining bright! ✨",
    "Effort leads to excellence, and you're on your way! Awesome job! 🎉",
    "The hard work you’re putting in now will pay off—keep it up! 🥇",
    "Small steps lead to great achievements—keep moving forward! 🚶‍♀️",
    "Stay focused and persistent—you're closer to your goals than you think! 🎯",
    "You're an inspiration! Keep showing everyone what you're capable of! 🌟",
    "No matter the obstacles, you're making progress. Keep climbing! 🏔️",
    "You’re proving your commitment with every submission—well done! 🏅",
    "Your determination is incredible! Keep reaching for the stars! 🌌",
    "Excellence is a habit, and you're building it daily. Great job! 🏆",
    "Your potential is limitless—keep aiming high! 🚀",
    "You're crafting a future filled with success. Keep at it! ✨",
    "Success is yours to claim—you're on the path to greatness! 🏅",
    "You're creating a masterpiece of success—one step at a time. 🎨",
    "Believe in your journey—every effort adds up to something amazing! 🌈",
    "You're achieving what many only dream of—keep at it! 💫",
    "Each step forward is a victory—celebrate your progress! 🎉",
    "You're unstoppable—keep proving what you're capable of! 🚀",
    "Keep dreaming big and working hard—you’re going places! 🌟",
    "Your effort today is paving the way for a brighter tomorrow! 🌅",
    "You're becoming stronger and smarter with every challenge—keep it up! 💡",
    "Great things are ahead—keep walking your path with confidence! 🌠",
    "Success loves persistence, and you're showing plenty of it! 💪",
    "You're creating your own story of success—keep writing it! ✍️",
    "The journey is as important as the destination—keep enjoying it! 🌈",
    "Believe in yourself and all that you are—you’re doing amazing! ✨",
    "Every step you take is building your confidence—keep going! 🏃",
    "You're turning hard work into achievements—fantastic job! 🏆",
    "You're proving that effort creates results—keep shining! 🌟",
    "Your dedication is paving the way for a bright future! 🌅",
    "Great things never come from comfort zones—you're doing great! 💡",
    "Your hard work and determination are inspiring—keep it up! 🚀",
    "You’re unstoppable—keep achieving those milestones! 🌠",
    "Every bit of effort adds up—your success is inevitable! 🌟",
    "Stay consistent, and the results will amaze you—well done! 🏅",
    "Keep reaching higher—you're creating something incredible! 🌌",
    "You're unstoppable—keep climbing the ladder of success! 🪜",
    "The effort you’re putting in now will lead to big rewards! 🥇",
    "Every success starts with effort, and you’re giving it your all! 🌈",
    "You're writing your success story one step at a time—great work! ✍️",
    "Keep challenging yourself—you’re capable of amazing things! 🌟",
    "Your determination and focus are inspiring—keep going! 🚀",
    "Success is closer than you think—keep moving forward! 🎯",
    "You’re a star in the making—keep shining bright! 🌠",
    "The road to success is built with effort, and you're paving it! 🛤️",
    "You're doing great—keep turning effort into excellence! 🌟",
    "Every challenge you overcome is a step toward greatness! 💪",
    "You’re proving that effort creates success—well done! 🏆",
    "You’re building something amazing—keep adding to your success! 🧱",
    "Hard work pays off, and you're proof of that—keep it up! 💡",
    "Success is built daily—you're laying the foundation! 🚧",
    "Keep striving, keep thriving—you're doing incredible! 🌟",
    "You're proving that persistence and effort lead to greatness! 🏅",
    "The future looks bright for you—keep working hard! 🌅",
    "Your dedication is leading you to amazing places—keep going! 🚀",
    "Every step forward is a step toward your dreams—great job! 🌠",
    "You’re capable of achieving greatness—keep believing! 🌟",
    "Stay motivated, stay focused—you're achieving something special! ✨",
    "Your hard work is your superpower—keep using it! 💪",
    "Each day you improve—your progress is inspiring! 🌈",
    "You're unstoppable—keep moving toward success! 🌟",
    "Keep chasing your dreams—they're within your reach! 🌠",
    "You're doing fantastic—keep up the brilliant work! ✨",
    "Your success is inevitable—just keep moving forward! 🚶",
    "You’re capable of amazing things—keep proving it daily! 💡",
    "Every challenge you face makes you stronger—great job! 💪",
    "You're creating a future filled with possibilities—keep it up! 🌅",
    "You're achieving what others only dream of—fantastic job! 🌟",
    "Keep believing in your abilities—they’re taking you far! 🚀",
    "You're showing that effort creates results—keep at it! 🌌",
    "You’re reaching new heights—keep climbing! 🏔️",
    "The best is yet to come—keep striving for excellence! 🌅",
    "You’re building a foundation for greatness—keep going! 🏗️",
    "Keep taking steps forward—your success is waiting! 🌟",
    "You're turning hard work into success—keep it up! 🏆",
    "Stay determined—your persistence is inspiring! 💪",
    "Every effort is bringing you closer to success—great work! 🎯",
    "You’re capable of achieving amazing things—keep believing! 🌠",
    "The journey is just as important as the destination—enjoy it! 🌈",
    "You’re creating a future filled with success—keep going! 🚀",
    "Keep working hard—you’re proving that effort leads to greatness! ✨",
    "You’re doing fantastic—keep making those strides forward! 🌟",
    "Success is built on effort, and you're laying the groundwork! 🛠️",
    "Your future self will thank you for the effort you're putting in today! 🕒",
]


def calculate_delta_seconds(
    submission_time: str | datetime.datetime, due_date: str | datetime.datetime
) -> int:
    """
    Calculate the time delta between two timestamps in seconds.

    Args:
        submission_time (str): The first timestamp in the format "YYYY-MM-DD HH:MM:SS TZ".
        due_date (str): The second timestamp in the format "YYYY-MM-DD HH:MM:SS TZ".

    Returns:
        int: The time delta between the two timestamps in seconds.
    """

    # Parse timestamps into datetime objects if necessary
    submission_datetime = (
        date_parser.parse(submission_time)
        if isinstance(submission_time, str)
        else submission_time
    )
    due_datetime = (
        date_parser.parse(due_date) if isinstance(due_date, str) else due_date
    )

    # Add timezone (default UTC) if not present
    if submission_datetime.tzinfo is None:
        submission_datetime = submission_datetime.replace(tzinfo=datetime.UTC)
    if due_datetime.tzinfo is None:
        due_datetime = due_datetime.replace(tzinfo=datetime.UTC)

    time_delta = submission_datetime - due_datetime

    # Return time delta in seconds, as int
    return int(time_delta.total_seconds())


def get_key_box() -> Box:
    """
    Generate a public/private keypair for use with NaCl.

    Returns:
        tuple[PublicKey, PrivateKey]: A tuple containing the public and private keys.
    """
    server_private_key_b64 = os.getenv("SERVER_PRIVATE_KEY")
    client_public_key_b64 = os.getenv("CLIENT_PUBLIC_KEY")

    if not server_private_key_b64 or not client_public_key_b64:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server or client key not found",
        )

    server_private_key = PrivateKey(base64.b64decode(server_private_key_b64))
    client_public_key = PublicKey(base64.b64decode(client_public_key_b64))

    box = Box(server_private_key, client_public_key)

    return box


def get_grade_modifier(time_delta: int) -> float:
    """
    Calculate the grade modifier based on the time delta between two timestamps.

    Args:
        time_delta (int): The time delta between two timestamps in seconds.

    Returns:
        float: The grade modifier percentage based on the time delta.
    """

    # Parameters
    Q0 = 100  # Initial quantity
    Q_min = 40  # Minimum grade/quantity
    k = 6.88e-5  # Decay constant per minute

    # Exponential decay function with piecewise definition
    Q: float = Q0 * np.exp(-k * time_delta / 60)  # Convert seconds to minutes
    Q = np.maximum(Q, Q_min)  # Apply floor condition
    Q = np.minimum(Q, 100)  # Apply ceiling condition

    return Q
