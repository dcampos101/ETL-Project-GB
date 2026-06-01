-- Tabla Departments
CREATE TABLE Departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

-- Tabla Jobs
CREATE TABLE Jobs (
    job_id SERIAL PRIMARY KEY,
    job_title VARCHAR(100) NOT NULL
);

-- Tabla HiredEmployees
CREATE TABLE HiredEmployees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hire_date TIMESTAMP NOT NULL,  -- conserva fecha y hora
    department_id INT NOT NULL,
    job_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id),
    FOREIGN KEY (job_id) REFERENCES Jobs(job_id)
);
