"""Exercises: ORM fundamentals.

Implement the TODO functions. Autograder will test them.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from src.exercises.extensions import db
from src.exercises.models import Student, Grade, Assignment


# ===== BASIC CRUD =====

def create_student(name: str, email: str) -> Student:
    created_student = Student(name=name, email=email)
    try:
        db.session.add(created_student)
        db.session.commit()
        return created_student
    except IntegrityError:
        db.session.rollback()
        raise ValueError("duplicate email")



def find_student_by_email(email: str) -> Optional[Student]:
    found = db.session.query(Student).filter(Student.email == email).one_or_none()
    return found


def add_grade(student_id: int, assignment_id: int, score: int) -> Grade:
    student = db.session.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise LookupError("student doesn't exist")
    assignment = db.session.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise LookupError("assignment doesn't exist")
    exists = db.session.query(Grade).filter(Grade.student_id == student.id, Grade.assignment_id == assignment_id).first()
    if exists:
        raise ValueError("duplicate grade")
    grade = Grade(student=student, assignment=assignment, score=score)
    db.session.add(grade)
    db.session.commit()
    return grade


def average_percent(student_id: int) -> float:
    student = db.session.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise LookupError("No such student.")
    grades = db.session.query(Grade).filter(Grade.student_id == student_id).all()
    if not grades:
        return 0.0
    total =0
    for g in grades:
        percent = g.score / g.assignment.max_points * 100
        total += percent
    avg = total/len(grades)
    return avg



# ===== QUERYING & FILTERING =====

def get_all_students() -> list[Student]:
    students = db.session.query(Student).order_by(Student.name).all()
    return students


def get_assignment_by_title(title: str) -> Optional[Assignment]:
    return db.session.query(Assignment).filter(Assignment.title == title).one_or_none()


def get_student_grades(student_id: int) -> list[Grade]:
    student = db.session.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise LookupError("student doesn't exist")
    grades = db.session.query(Grade).join(Assignment).filter(Grade.student_id == student.id).order_by(Assignment.title).all()
    return grades


def get_grades_for_assignment(assignment_id: int) -> list[Grade]:
    assignment = db.session.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise LookupError("assignment doesn't exist")
    grades = db.session.query(Grade).join(Student).filter(Grade.assignment_id == assignment.id).order_by(Student.name).all()
    return grades


# ===== AGGREGATION =====

def total_student_grade_count() -> int:
    count = db.session.query(Grade).count()
    return count


def highest_score_on_assignment(assignment_id: int) -> Optional[int]:
    assignment = db.session.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise LookupError("assignment doesn't exist")
    high = db.session.query(func.max(Grade.score).filter(Grade.assignment_id == assignment_id)).scalar()
    return high


def class_average_percent() -> float:
    avg = db.session.query(func.avg(Grade.score/Assignment.max_points*100)).join(Assignment).scalar()
    if not avg:
        avg = 0.0
    return avg


def student_grade_count(student_id: int) -> int:
    student = db.session.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise LookupError("student doesn't exist")
    num = db.session.query(Grade).filter(Grade.student_id == student.id).count()
    return num


# ===== UPDATING & DELETION =====

def update_student_email(student_id: int, new_email: str) -> Student:
    student = db.session.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise LookupError("student doesn't exist")
    exist = db.session.query(Student).filter(Student.email == new_email).first()
    if exist:
        db.session.rollback()
        raise ValueError("duplicate email")
    student.email = new_email
    db.session.commit()
    return student


def delete_student(student_id: int) -> None:
    student = db.session.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise LookupError("student doesn't exist")
    db.session.delete(student)
    db.session.commit()


def delete_grade(grade_id: int) -> None:
    grade = db.session.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise LookupError("grade doesn't exist")
    db.session.delete(grade)
    db.session.commit()



# ===== FILTERING & FILTERING WITH AGGREGATION =====

def students_with_average_above(threshold: float) -> list[Student]:
    avg = func.avg(Grade.score/Assignment.max_points*100)
    students = db.session.query(Student).join(Grade).join(Assignment).group_by(Student.id).having(avg > threshold).order_by(avg.desc()).all()
    return students


def assignments_without_grades() -> list[Assignment]:
    none = db.session.query(Assignment).outerjoin(Grade).filter(Grade.assignment_id == None).order_by(Assignment.title).all()
    return none


def top_scorer_on_assignment(assignment_id: int) -> Optional[Student]:
    assignment = db.session.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise LookupError("assignment doesn't exist")
    high = db.session.query(Student).join(Grade).filter(Grade.assignment_id == assignment.id).order_by(Grade.score.desc()).first()
    return high

