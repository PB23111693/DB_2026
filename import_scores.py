import json
from models import db
from sqlalchemy import text
from app import create_app

app = create_app()

# ======== 第一个学期的成绩数据（2024-2025-1） ========
scores_semester1 = [
    {"stu_id": "2024001", "course_id": "CS101", "regular": 88, "final": 92, "total": 90, "exam": "考试"},
    {"stu_id": "2024001", "course_id": "CS102", "regular": 76, "final": 80, "total": 78, "exam": "考试"},
    {"stu_id": "2024001", "course_id": "MATH101", "regular": 85, "final": 88, "total": 87, "exam": "考试"},
    {"stu_id": "2024002", "course_id": "CS101", "regular": 60, "final": 55, "total": 58, "exam": "考试"},
    {"stu_id": "2024002", "course_id": "MATH101", "regular": 95, "final": 93, "total": 94, "exam": "考试"},
    {"stu_id": "2024003", "course_id": "CS101", "regular": 72, "final": 68, "total": 70, "exam": "考试"},
    {"stu_id": "2024003", "course_id": "CS201", "regular": 82, "final": 78, "total": 80, "exam": "考查"},
    {"stu_id": "2024004", "course_id": "MATH101", "regular": 91, "final": 89, "total": 90, "exam": "考试"},
    {"stu_id": "2024004", "course_id": "MATH102", "regular": 65, "final": 70, "total": 68, "exam": "考试"},
    {"stu_id": "2024005", "course_id": "PHY101", "regular": 77, "final": 73, "total": 75, "exam": "考查"},
    {"stu_id": "2024005", "course_id": "MATH101", "regular": 80, "final": 85, "total": 83, "exam": "考试"},
    {"stu_id": "2024006", "course_id": "EE101", "regular": 88, "final": 92, "total": 90, "exam": "考试"},
    {"stu_id": "2024006", "course_id": "MATH101", "regular": 70, "final": 68, "total": 69, "exam": "考试"},
]

# ======== 第二个学期的成绩数据（2024-2025-2） ========
scores_semester2 = [
    {"stu_id": "2024001", "course_id": "CS201", "regular": 78, "final": 82, "total": 80, "exam": "考试"},
    {"stu_id": "2024001", "course_id": "MATH102", "regular": 70, "final": 75, "total": 73, "exam": "考试"},
    {"stu_id": "2024002", "course_id": "CS102", "regular": 85, "final": 90, "total": 88, "exam": "考试"},
    {"stu_id": "2024002", "course_id": "PHY101", "regular": 60, "final": 62, "total": 61, "exam": "考查"},
    {"stu_id": "2024003", "course_id": "MATH102", "regular": 92, "final": 88, "total": 90, "exam": "考试"},
    {"stu_id": "2024004", "course_id": "PHY101", "regular": 55, "final": 60, "total": 58, "exam": "考查"},
    {"stu_id": "2024004", "course_id": "EE101", "regular": 80, "final": 78, "total": 79, "exam": "考试"},
    {"stu_id": "2024005", "course_id": "CS101", "regular": 88, "final": 85, "total": 86, "exam": "考试"},
    {"stu_id": "2024006", "course_id": "CS101", "regular": 65, "final": 70, "total": 68, "exam": "考试"},
    {"stu_id": "2024006", "course_id": "MATH102", "regular": 75, "final": 80, "total": 78, "exam": "考试"},
]

with app.app_context():
    with db.engine.begin() as conn:
        # 导入第一个学期的成绩
        conn.execute(
            text("CALL sp_import_scores(:data, :semester)"),
            {"data": json.dumps(scores_semester1), "semester": "2024-2025-1"}
        )
        print(f"已导入 {len(scores_semester1)} 条成绩到学期 2024-2025-1")

        # 导入第二个学期的成绩
        conn.execute(
            text("CALL sp_import_scores(:data, :semester)"),
            {"data": json.dumps(scores_semester2), "semester": "2024-2025-2"}
        )
        print(f"已导入 {len(scores_semester2)} 条成绩到学期 2024-2025-2")

print("所有成绩批量导入完成！请查询 score、enrollment、student_summary 表验证。")