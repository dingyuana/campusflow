# 智慧校园业务数据库设计

## 📋 概述

本文档描述了 CampusFlow 项目的业务数据库表结构设计，使用 Supabase（PostgreSQL）作为数据库。

---

## 🗄️ 数据库表结构

### 1. students（学生表）

**用途**：存储学生基本信息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 学生 ID |
| student_id | VARCHAR(20) | UNIQUE NOT NULL | 学号 |
| name | VARCHAR(100) | NOT NULL | 姓名 |
| gender | VARCHAR(10) |  | 性别 |
| birth_date | DATE |  | 出生日期 |
| department_code | VARCHAR(20) | FK → departments | 所属院系代码 |
| major | VARCHAR(100) |  | 专业 |
| grade | VARCHAR(20) |  | 年级 |
| class_name | VARCHAR(50) |  | 班级 |
| phone | VARCHAR(20) |  | 联系电话 |
| email | VARCHAR(100) |  | 邮箱 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态：active/suspended/graduated |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引**：
- `idx_student_id`: student_id
- `idx_department_code`: department_code
- `idx_status`: status

**SQL**：
```sql
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    birth_date DATE,
    department_code VARCHAR(20) REFERENCES departments(code),
    major VARCHAR(100),
    grade VARCHAR(20),
    class_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_student_id ON students(student_id);
CREATE INDEX idx_department_code ON students(department_code);
CREATE INDEX idx_status ON students(status);
```

---

### 2. teachers（教师表）

**用途**：存储教师基本信息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 教师 ID |
| teacher_id | VARCHAR(20) | UNIQUE NOT NULL | 教师工号 |
| name | VARCHAR(100) | NOT NULL | 姓名 |
| gender | VARCHAR(10) |  | 性别 |
| title | VARCHAR(50) |  | 职称（教授/副教授等） |
| department_code | VARCHAR(20) | FK → departments | 所属院系代码 |
| phone | VARCHAR(20) |  | 联系电话 |
| email | VARCHAR(100) |  | 邮箱 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引**：
- `idx_teacher_id`: teacher_id
- `idx_department_code`: department_code
- `idx_status`: status

**SQL**：
```sql
CREATE TABLE teachers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    title VARCHAR(50),
    department_code VARCHAR(20) REFERENCES departments(code),
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_teacher_id ON teachers(teacher_id);
CREATE INDEX idx_department_code ON teachers(department_code);
CREATE INDEX idx_status ON teachers(status);
```

---

### 3. departments（院系表）

**用途**：存储院系信息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 院系 ID |
| code | VARCHAR(20) | UNIQUE NOT NULL | 院系代码 |
| name | VARCHAR(100) | NOT NULL | 院系名称 |
| dean | VARCHAR(100) |  | 院长 |
| phone | VARCHAR(20) |  | 联系电话 |
| location | VARCHAR(200) |  | 办公地点 |
| description | TEXT |  | 描述 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引**：
- `idx_code`: code

**SQL**：
```sql
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    dean VARCHAR(100),
    phone VARCHAR(20),
    location VARCHAR(200),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_code ON departments(code);
```

---

### 4. courses（课程表）

**用途**：存储课程信息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 课程 ID |
| course_id | VARCHAR(20) | UNIQUE NOT NULL | 课程代码 |
| name | VARCHAR(200) | NOT NULL | 课程名称 |
| credit | INTEGER | NOT NULL | 学分 |
| hours | INTEGER |  | 学时 |
| course_type | VARCHAR(20) |  | 课程类型：required/elective |
| description | TEXT |  | 课程描述 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引**：
- `idx_course_id`: course_id

**SQL**：
```sql
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    credit INTEGER NOT NULL,
    hours INTEGER,
    course_type VARCHAR(20),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_course_id ON courses(course_id);
```

---

### 5. enrollments（选课表）

**用途**：存储学生选课记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 选课 ID |
| student_id | UUID | FK → students | 学生 ID |
| course_id | UUID | FK → courses | 课程 ID |
| semester | VARCHAR(20) | NOT NULL | 学期（如 2024春） |
| score | DECIMAL(5,2) |  | 成绩 |
| status | VARCHAR(20) | DEFAULT 'enrolled' | 状态：enrolled/completed/dropped |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引**：
- `idx_student_id`: student_id
- `idx_course_id`: course_id
- `idx_semester`: semester
- `unique_enrollment`: (student_id, course_id, semester)

**SQL**：
```sql
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    course_id UUID REFERENCES courses(id),
    semester VARCHAR(20) NOT NULL,
    score DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'enrolled',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, course_id, semester)
);

CREATE INDEX idx_student_id ON enrollments(student_id);
CREATE INDEX idx_course_id ON enrollments(course_id);
CREATE INDEX idx_semester ON enrollments(semester);
```

---

### 6. schedules（课程表）

**用途**：存储课程安排

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 课程安排 ID |
| course_id | UUID | FK → courses | 课程 ID |
| teacher_id | UUID | FK → teachers | 教师 ID |
| classroom | VARCHAR(100) |  | 教室 |
| day_of_week | VARCHAR(10) | NOT NULL | 星期几 |
| start_time | TIME | NOT NULL | 开始时间 |
| end_time | TIME | NOT NULL | 结束时间 |
| semester | VARCHAR(20) | NOT NULL | 学期 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引**：
- `idx_course_id`: course_id
- `idx_teacher_id`: teacher_id
- `idx_semester`: semester
- `idx_day_of_week`: day_of_week

**SQL**：
```sql
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id),
    teacher_id UUID REFERENCES teachers(id),
    classroom VARCHAR(100),
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    semester VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_course_id ON schedules(course_id);
CREATE INDEX idx_teacher_id ON schedules(teacher_id);
CREATE INDEX idx_semester ON schedules(semester);
CREATE INDEX idx_day_of_week ON schedules(day_of_week);
```

---

## 📊 表关系图

```
departments (院系)
    ↑
    | department_code
    |
    +-- students (学生) ← enrollments (选课) ← courses (课程)
    |
    +-- teachers (教师)
            ↑
            | teacher_id
            |
        schedules (课程表)
```

---

## 🚀 初始化数据

```sql
-- 插入院系数据
INSERT INTO departments (code, name, dean, phone, location) VALUES
('CS', '计算机学院', '张教授', '010-12345678', '计算机楼'),
('MATH', '数学学院', '李教授', '010-87654321', '数学楼'),
('PHYS', '物理学院', '王教授', '010-11112222', '物理楼');

-- 插入教师数据
INSERT INTO teachers (teacher_id, name, gender, title, department_code, phone, email) VALUES
('T001', '张教授', '男', '教授', 'CS', '13800138000', 'zhang@example.com'),
('T002', '李教授', '女', '副教授', 'MATH', '13800138001', 'li@example.com'),
('T003', '王教授', '男', '副教授', 'CS', '13800138002', 'wang@example.com');

-- 插入学生数据
INSERT INTO students (student_id, name, gender, birth_date, department_code, major, grade, class_name, phone, email) VALUES
('S001', '张三', '男', '2003-01-01', 'CS', '计算机科学与技术', '2024', '计科2401', '13900139000', 'zhangsan@example.com'),
('S002', '李四', '女', '2003-02-01', 'CS', '软件工程', '2024', '软工2401', '13900139001', 'lisi@example.com'),
('S003', '王五', '男', '2003-03-01', 'MATH', '应用数学', '2024', '应数2401', '13900139002', 'wangwu@example.com'),
('S004', '赵六', '女', '2003-04-01', 'PHYS', '物理学', '2024', '物理2401', '13900139003', 'zhaoliu@example.com');

-- 插入课程数据
INSERT INTO courses (course_id, name, credit, hours, course_type, description) VALUES
('C001', 'Python 程序设计', 3, 48, 'required', 'Python 编程基础'),
('C002', '数据结构', 4, 64, 'required', '数据结构与算法'),
('C003', '高等数学', 5, 80, 'required', '高等数学基础'),
('C004', '机器学习', 3, 48, 'elective', '机器学习导论');

-- 插入选课数据
INSERT INTO enrollments (student_id, course_id, semester, status) VALUES
((SELECT id FROM students WHERE student_id = 'S001'), (SELECT id FROM courses WHERE course_id = 'C001'), '2024春', 'enrolled'),
((SELECT id FROM students WHERE student_id = 'S001'), (SELECT id FROM courses WHERE course_id = 'C002'), '2024春', 'enrolled'),
((SELECT id FROM students WHERE student_id = 'S002'), (SELECT id FROM courses WHERE course_id = 'C001'), '2024春', 'enrolled'),
((SELECT id FROM students WHERE student_id = 'S002'), (SELECT id FROM courses WHERE course_id = 'C004'), '2024春', 'enrolled'),
((SELECT id FROM students WHERE student_id = 'S003'), (SELECT id FROM courses WHERE course_id = 'C003'), '2024春', 'enrolled'),
((SELECT id FROM students WHERE student_id = 'S004'), (SELECT id FROM courses WHERE course_id = 'C002'), '2024春', 'enrolled');

-- 插入课程表数据
INSERT INTO schedules (course_id, teacher_id, classroom, day_of_week, start_time, end_time, semester) VALUES
((SELECT id FROM courses WHERE course_id = 'C001'), (SELECT id FROM teachers WHERE teacher_id = 'T001'), 'A101', '周一', '08:00', '09:40', '2024春'),
((SELECT id FROM courses WHERE course_id = 'C002'), (SELECT id FROM teachers WHERE teacher_id = 'T003'), 'A102', '周二', '10:00', '11:40', '2024春'),
((SELECT id FROM courses WHERE course_id = 'C003'), (SELECT id FROM teachers WHERE teacher_id = 'T002'), 'B201', '周三', '14:00', '15:40', '2024春'),
((SELECT id FROM courses WHERE course_id = 'C004'), (SELECT id FROM teachers WHERE teacher_id = 'T001'), 'C301', '周四', '16:00', '17:40', '2024春');
```

---

## 📝 注意事项

1. **UUID 生成**：需要启用 `uuid-ossp` 扩展
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

2. **外键约束**：确保相关表存在后再创建外键

3. **索引优化**：根据查询模式添加合适的索引

4. **数据类型**：使用合适的数据类型，避免存储空间浪费

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
