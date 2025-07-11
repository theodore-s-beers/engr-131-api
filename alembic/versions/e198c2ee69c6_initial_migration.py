"""Initial migration

Revision ID: e198c2ee69c6
Revises:
Create Date: 2024-09-23 16:55:35.561225

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e198c2ee69c6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assignments_title"), "assignments", ["title"], unique=True)
    op.create_table(
        "exams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exams_title"), "exams", ["title"], unique=True)
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("given_name", sa.String(), nullable=False),
        sa.Column("family_name", sa.String(), nullable=False),
        sa.Column("lecture_section", sa.Integer(), nullable=True),
        sa.Column("lab_section", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_students_email"), "students", ["email"], unique=True)
    op.create_index(
        op.f("ix_students_lab_section"), "students", ["lab_section"], unique=False
    )
    op.create_index(
        op.f("ix_students_lecture_section"),
        "students",
        ["lecture_section"],
        unique=False,
    )
    op.create_table(
        "assignment_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_email", sa.String(), nullable=False),
        sa.Column("assignment_id", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["assignments.id"],
        ),
        sa.ForeignKeyConstraint(
            ["student_email"],
            ["students.email"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "exam_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_email", sa.String(), nullable=False),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exam_id"],
            ["exams.id"],
        ),
        sa.ForeignKeyConstraint(
            ["student_email"],
            ["students.email"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "logins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("role", sa.Enum("ADMIN", "STUDENT", name="role"), nullable=False),
        sa.Column("ip_address", sa.String(), nullable=False),
        sa.Column("student_email", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["student_email"],
            ["students.email"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("logins")
    op.drop_table("exam_submissions")
    op.drop_table("assignment_submissions")
    op.drop_index(op.f("ix_students_lecture_section"), table_name="students")
    op.drop_index(op.f("ix_students_lab_section"), table_name="students")
    op.drop_index(op.f("ix_students_email"), table_name="students")
    op.drop_table("students")
    op.drop_index(op.f("ix_exams_title"), table_name="exams")
    op.drop_table("exams")
    op.drop_index(op.f("ix_assignments_title"), table_name="assignments")
    op.drop_table("assignments")
    # ### end Alembic commands ###
