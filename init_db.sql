-- =====================================================
-- 学籍管理系统 数据库初始化脚本（完整版，含测试数据）
-- =====================================================
CREATE DATABASE IF NOT EXISTS xueji_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE xueji_db;

-- ------------------------- 建表 -------------------------
CREATE TABLE department (
    dept_id   VARCHAR(10) PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL,
    dean      VARCHAR(20),
    phone     VARCHAR(20),
    office    VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE major (
    major_id    VARCHAR(10) PRIMARY KEY,
    major_name  VARCHAR(50) NOT NULL,
    dept_id     VARCHAR(10) NOT NULL,
    duration    TINYINT,
    degree_type VARCHAR(20),
    leader_id   VARCHAR(20) COMMENT '负责人教师工号',
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE classes (
    class_id   VARCHAR(10) PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    major_id   VARCHAR(10) NOT NULL,
    counselor_id VARCHAR(20) COMMENT '辅导员教师工号',
    grade      YEAR,
    FOREIGN KEY (major_id) REFERENCES major(major_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE student (
    stu_id            VARCHAR(20) PRIMARY KEY,
    name              VARCHAR(30) NOT NULL,
    gender            CHAR(1),
    birth             DATE,
    ethnicity         VARCHAR(20),
    political_status  VARCHAR(20),
    native_place      VARCHAR(50),
    id_card           CHAR(18),
    phone             VARCHAR(20),
    email             VARCHAR(50),
    address           VARCHAR(100),
    enrollment_year   YEAR,
    status            VARCHAR(10) DEFAULT '在读',
    photo_path        VARCHAR(200),
    resume_path       VARCHAR(200),
    class_id          VARCHAR(10) NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE major_change (
    change_id     INT AUTO_INCREMENT PRIMARY KEY,
    stu_id        VARCHAR(20) NOT NULL,
    origin_major  VARCHAR(10),
    new_major     VARCHAR(10),
    change_date   DATE NOT NULL,
    approval_doc  VARCHAR(50),
    reason        VARCHAR(200),
    operator      VARCHAR(20),
    FOREIGN KEY (stu_id) REFERENCES student(stu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE award (
    award_id         INT AUTO_INCREMENT PRIMARY KEY,
    stu_id           VARCHAR(20) NOT NULL,
    award_name       VARCHAR(50) NOT NULL,
    award_level      VARCHAR(20),
    award_date       DATE NOT NULL,
    issuer           VARCHAR(50),
    certificate_path VARCHAR(200),
    FOREIGN KEY (stu_id) REFERENCES student(stu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE punishment (
    punish_id   INT AUTO_INCREMENT PRIMARY KEY,
    stu_id      VARCHAR(20) NOT NULL,
    punish_type VARCHAR(20) NOT NULL,
    punish_date DATE NOT NULL,
    reason      VARCHAR(200),
    lift_date   DATE,
    file_path   VARCHAR(200),
    FOREIGN KEY (stu_id) REFERENCES student(stu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE course (
    course_id     VARCHAR(10) PRIMARY KEY,
    course_name   VARCHAR(50) NOT NULL,
    credit        DECIMAL(3,1),
    hours         SMALLINT,
    dept_id       VARCHAR(10) NOT NULL,
    course_type   VARCHAR(10),
    syllabus_path VARCHAR(200),
    teacher_id    VARCHAR(20) COMMENT '授课教师工号',
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE enrollment (
    enroll_id   INT AUTO_INCREMENT PRIMARY KEY,
    stu_id      VARCHAR(20) NOT NULL,
    course_id   VARCHAR(10) NOT NULL,
    semester    VARCHAR(20) NOT NULL,
    enroll_date DATE,
    FOREIGN KEY (stu_id)    REFERENCES student(stu_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    UNIQUE KEY uk_sc (stu_id, course_id, semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE score (
    score_id      INT AUTO_INCREMENT PRIMARY KEY,
    enroll_id     INT NOT NULL UNIQUE,
    regular_score DECIMAL(5,2),
    final_score   DECIMAL(5,2),
    total_score   DECIMAL(5,2),
    exam_method   VARCHAR(10),
    makeup_score  DECIMAL(5,2),
    FOREIGN KEY (enroll_id) REFERENCES enrollment(enroll_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE student_summary (
    stu_id        VARCHAR(20) PRIMARY KEY,
    total_credits DECIMAL(5,1) DEFAULT 0,
    gpa           DECIMAL(4,2) DEFAULT 0,
    has_punish    BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (stu_id) REFERENCES student(stu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(30) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(10) NOT NULL,
    name          VARCHAR(30),
    dept_id       VARCHAR(10),
    related_id    VARCHAR(20),
    last_login    DATETIME,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------- 函数 -------------------------
DELIMITER $$

CREATE FUNCTION fn_calc_student_gpa(p_stu_id VARCHAR(20))
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_credits DECIMAL(5,1);
    DECLARE weighted_score DECIMAL(10,2);
    SELECT SUM(c.credit),
           SUM(c.credit * CASE
               WHEN s.total_score >= 90 THEN 4.0
               WHEN s.total_score >= 85 THEN 3.7
               WHEN s.total_score >= 82 THEN 3.3
               WHEN s.total_score >= 78 THEN 3.0
               WHEN s.total_score >= 75 THEN 2.7
               WHEN s.total_score >= 72 THEN 2.3
               WHEN s.total_score >= 68 THEN 2.0
               WHEN s.total_score >= 65 THEN 1.7
               WHEN s.total_score >= 64 THEN 1.5
               WHEN s.total_score >= 61 THEN 1.3
               WHEN s.total_score >= 60 THEN 1.0
               ELSE 0 END)
    INTO total_credits, weighted_score
    FROM score s
    JOIN enrollment e ON s.enroll_id = e.enroll_id
    JOIN course c ON e.course_id = c.course_id
    WHERE e.stu_id = p_stu_id AND s.total_score IS NOT NULL;
    IF total_credits IS NULL OR total_credits = 0 THEN RETURN 0;
    ELSE RETURN ROUND(weighted_score / total_credits, 2);
    END IF;
END $$

CREATE FUNCTION fn_can_graduate(p_stu_id VARCHAR(20))
RETURNS BOOLEAN
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(5,1);
    DECLARE v_gpa DECIMAL(5,2);
    SELECT total_credits, gpa INTO v_total, v_gpa FROM student_summary WHERE stu_id = p_stu_id;
    RETURN (v_total >= 130 AND v_gpa >= 2.0);
END $$

-- ------------------------- 触发器 -------------------------
CREATE TRIGGER trg_student_after_insert
AFTER INSERT ON student
FOR EACH ROW
BEGIN
    INSERT INTO student_summary (stu_id) VALUES (NEW.stu_id)
    ON DUPLICATE KEY UPDATE stu_id = NEW.stu_id;
END $$

CREATE TRIGGER trg_score_after_change
AFTER INSERT ON score
FOR EACH ROW
BEGIN
    DECLARE v_stu_id VARCHAR(20);
    SELECT stu_id INTO v_stu_id FROM enrollment WHERE enroll_id = NEW.enroll_id;
    UPDATE student_summary SET
        gpa = fn_calc_student_gpa(v_stu_id),
        total_credits = (SELECT COALESCE(SUM(c.credit),0)
                         FROM score s JOIN enrollment e ON s.enroll_id = e.enroll_id
                         JOIN course c ON e.course_id = c.course_id
                         WHERE e.stu_id = v_stu_id AND s.total_score >= 60)
    WHERE stu_id = v_stu_id;
END $$

CREATE TRIGGER trg_score_after_update
AFTER UPDATE ON score
FOR EACH ROW
BEGIN
    DECLARE v_stu_id VARCHAR(20);
    SELECT stu_id INTO v_stu_id FROM enrollment WHERE enroll_id = NEW.enroll_id;
    UPDATE student_summary SET
        gpa = fn_calc_student_gpa(v_stu_id),
        total_credits = (SELECT COALESCE(SUM(c.credit),0)
                         FROM score s JOIN enrollment e ON s.enroll_id = e.enroll_id
                         JOIN course c ON e.course_id = c.course_id
                         WHERE e.stu_id = v_stu_id AND s.total_score >= 60)
    WHERE stu_id = v_stu_id;
END $$

CREATE TRIGGER trg_punishment_after_insert
AFTER INSERT ON punishment
FOR EACH ROW
BEGIN
    IF NEW.lift_date IS NULL OR NEW.lift_date > CURDATE() THEN
        UPDATE student_summary SET has_punish = TRUE WHERE stu_id = NEW.stu_id;
    END IF;
END $$

CREATE TRIGGER trg_punishment_after_update
AFTER UPDATE ON punishment
FOR EACH ROW
BEGIN
    IF NEW.lift_date IS NOT NULL AND NEW.lift_date <= CURDATE() THEN
        IF NOT EXISTS (SELECT 1 FROM punishment WHERE stu_id = NEW.stu_id AND (lift_date IS NULL OR lift_date > CURDATE())) THEN
            UPDATE student_summary SET has_punish = FALSE WHERE stu_id = NEW.stu_id;
        END IF;
    END IF;
END $$

-- ------------------------- 存储过程 -------------------------
CREATE PROCEDURE sp_import_scores(
    IN score_data JSON,
    IN p_semester VARCHAR(20)
)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE n INT DEFAULT JSON_LENGTH(score_data);
    DECLARE v_stu_id VARCHAR(20);
    DECLARE v_course_id VARCHAR(10);
    DECLARE v_exam VARCHAR(10);
    DECLARE v_regular, v_final, v_total DECIMAL(5,2);
    DECLARE v_enroll_id INT;
    WHILE i < n DO
        SET v_stu_id = JSON_UNQUOTE(JSON_EXTRACT(score_data, CONCAT('$[', i, '].stu_id')));
        SET v_course_id = JSON_UNQUOTE(JSON_EXTRACT(score_data, CONCAT('$[', i, '].course_id')));
        SET v_regular = JSON_EXTRACT(score_data, CONCAT('$[', i, '].regular'));
        SET v_final = JSON_EXTRACT(score_data, CONCAT('$[', i, '].final'));
        SET v_total = JSON_EXTRACT(score_data, CONCAT('$[', i, '].total'));
        SET v_exam = JSON_UNQUOTE(JSON_EXTRACT(score_data, CONCAT('$[', i, '].exam')));
        SELECT enroll_id INTO v_enroll_id
        FROM enrollment
        WHERE stu_id = v_stu_id AND course_id = v_course_id AND semester = p_semester;
        IF v_enroll_id IS NULL THEN
            INSERT INTO enrollment (stu_id, course_id, semester, enroll_date)
            VALUES (v_stu_id, v_course_id, p_semester, CURDATE());
            SET v_enroll_id = LAST_INSERT_ID();
        END IF;
        INSERT INTO score (enroll_id, regular_score, final_score, total_score, exam_method)
        VALUES (v_enroll_id, v_regular, v_final, v_total, v_exam)
        ON DUPLICATE KEY UPDATE
            regular_score = v_regular,
            final_score   = v_final,
            total_score   = v_total,
            exam_method   = v_exam;
        SET i = i + 1;
    END WHILE;
END $$

CREATE PROCEDURE sp_change_major(
    IN p_stu_id VARCHAR(20), IN p_new_major_id VARCHAR(10),
    IN p_change_date DATE, IN p_approval_doc VARCHAR(50),
    IN p_reason VARCHAR(200), IN p_operator VARCHAR(20))
BEGIN
    DECLARE v_old_major_id VARCHAR(10);
    DECLARE v_new_class_id VARCHAR(10);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    SELECT m.major_id INTO v_old_major_id
    FROM student st JOIN classes c ON st.class_id = c.class_id
    JOIN major m ON c.major_id = m.major_id
    WHERE st.stu_id = p_stu_id;
    IF v_old_major_id = p_new_major_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '新专业与当前专业相同，无法变更';
    END IF;
    SELECT class_id INTO v_new_class_id FROM classes WHERE major_id = p_new_major_id LIMIT 1;
    IF v_new_class_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '新专业无可用班级';
    END IF;
    INSERT INTO major_change (stu_id, origin_major, new_major, change_date, approval_doc, reason, operator)
    VALUES (p_stu_id, v_old_major_id, p_new_major_id, p_change_date, p_approval_doc, p_reason, p_operator);
    UPDATE student SET class_id = v_new_class_id WHERE stu_id = p_stu_id;
    COMMIT;
END $$

DELIMITER ;

-- ------------------------- 初始测试数据 -------------------------
-- 院系
INSERT INTO department VALUES
('CS', '计算机科学与技术学院', '张教授', '0551-63600001', '东区电三楼'),
('MATH', '数学科学学院', '李教授', '0551-63600002', '东区管理楼'),
('PHY', '物理学院', '王教授', '0551-63600003', '西区物理楼'),
('EE', '电子工程学院', '赵教授', '0551-63600004', '西区信息楼');

-- 用户（管理员默认由应用创建，此处创建教师和学生用户）
-- 密码均为 123456，哈希由应用生成，此处用占位，首次启动应用会自动修复
INSERT INTO users (username, password_hash, role, name, dept_id, related_id) VALUES
('teacher_zhang', 'scrypt:placeholder_will_be_updated_by_app', 'teacher', '张老师', 'CS', 'T001'),
('teacher_li', 'scrypt:placeholder_will_be_updated_by_app', 'teacher', '李老师', 'MATH', 'T002'),
('teacher_wang', 'scrypt:placeholder_will_be_updated_by_app', 'teacher', '王老师', 'PHY', 'T003'),
('teacher_zhao', 'scrypt:placeholder_will_be_updated_by_app', 'teacher', '赵老师', 'EE', 'T004'),
('2024001', 'scrypt:placeholder_will_be_updated_by_app', 'student', '李四', NULL, '2024001'),
('2024002', 'scrypt:placeholder_will_be_updated_by_app', 'student', '张三', NULL, '2024002'),
('2024003', 'scrypt:placeholder_will_be_updated_by_app', 'student', '王五', NULL, '2024003'),
('2024004', 'scrypt:placeholder_will_be_updated_by_app', 'student', '赵六', NULL, '2024004'),
('2024005', 'scrypt:placeholder_will_be_updated_by_app', 'student', '孙七', NULL, '2024005'),
('2024006', 'scrypt:placeholder_will_be_updated_by_app', 'student', '周八', NULL, '2024006');

-- 专业
INSERT INTO major VALUES
('CS01', '计算机科学与技术', 'CS', 4, '学士', 'T001'),
('CS02', '软件工程', 'CS', 4, '学士', 'T001'),
('MATH01', '数学与应用数学', 'MATH', 4, '学士', 'T002'),
('MATH02', '信息与计算科学', 'MATH', 4, '学士', 'T002'),
('PHY01', '物理学', 'PHY', 4, '学士', 'T003'),
('EE01', '电子信息工程', 'EE', 4, '学士', 'T004');

-- 班级
INSERT INTO classes VALUES
('CS2024A', '计科2024级1班', 'CS01', 'T001', 2024),
('CS2024B', '计科2024级2班', 'CS01', 'T001', 2024),
('CS2024C', '软工2024级1班', 'CS02', 'T001', 2024),
('MATH2024A', '数学2024级1班', 'MATH01', 'T002', 2024),
('PHY2024A', '物理2024级1班', 'PHY01', 'T003', 2024),
('EE2024A', '电子2024级1班', 'EE01', 'T004', 2024);

-- 学生
INSERT INTO student (stu_id, name, gender, birth, ethnicity, political_status, class_id, enrollment_year) VALUES
('2024001', '李四', 'F', '2004-03-15', '汉族', '团员', 'CS2024A', 2024),
('2024002', '张三', 'M', '2004-07-20', '汉族', '团员', 'CS2024A', 2024),
('2024003', '王五', 'M', '2004-01-10', '回族', '群众', 'CS2024B', 2024),
('2024004', '赵六', 'F', '2003-11-05', '汉族', '党员', 'MATH2024A', 2024),
('2024005', '孙七', 'M', '2004-05-22', '汉族', '团员', 'PHY2024A', 2024),
('2024006', '周八', 'F', '2004-09-30', '蒙古族', '团员', 'EE2024A', 2024);

-- 课程
INSERT INTO course VALUES
('CS101', '程序设计基础', 4, 64, 'CS', '必修', NULL, 'T001'),
('CS102', '数据结构', 4, 64, 'CS', '必修', NULL, 'T001'),
('CS201', '软件工程导论', 3, 48, 'CS', '必修', NULL, 'T001'),
('MATH101', '高等数学', 5, 80, 'MATH', '必修', NULL, 'T002'),
('MATH102', '线性代数', 4, 64, 'MATH', '必修', NULL, 'T002'),
('PHY101', '大学物理', 4, 64, 'PHY', '必修', NULL, 'T003'),
('EE101', '电路原理', 3, 48, 'EE', '必修', NULL, 'T004');

-- 选课（为学生选必修课）
INSERT INTO enrollment (stu_id, course_id, semester, enroll_date) VALUES
('2024001', 'CS101', '2024-2025-1', '2024-09-01'),
('2024001', 'CS102', '2024-2025-1', '2024-09-02'),
('2024001', 'MATH101', '2024-2025-1', '2024-09-03'),
('2024002', 'CS101', '2024-2025-1', '2024-09-01'),
('2024002', 'MATH101', '2024-2025-1', '2024-09-03'),
('2024003', 'CS101', '2024-2025-1', '2024-09-01'),
('2024003', 'CS201', '2024-2025-1', '2024-09-04'),
('2024004', 'MATH101', '2024-2025-1', '2024-09-01'),
('2024004', 'MATH102', '2024-2025-1', '2024-09-02'),
('2024005', 'PHY101', '2024-2025-1', '2024-09-01'),
('2024005', 'MATH101', '2024-2025-1', '2024-09-03'),
('2024006', 'EE101', '2024-2025-1', '2024-09-01'),
('2024006', 'MATH101', '2024-2025-1', '2024-09-03');

-- 成绩（为部分选课录入成绩）
INSERT INTO score (enroll_id, regular_score, final_score, total_score, exam_method) VALUES
(1, 85, 90, 88, '考试'),
(2, 78, 82, 80, '考试'),
(3, 92, 88, 90, '考试'),
(4, 70, 65, 68, '考试'),
(5, 60, 55, 58, '考试'),
(8, 95, 93, 94, '考试'),
(9, 80, 75, 78, '考试');