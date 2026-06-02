-- View for Report 1 (Hiring by Quarter)
CREATE OR REPLACE VIEW `etl-gb-poc.hresources.vw_hiring_quarter_2021` AS
SELECT 
          d.department_name,
          j.job_title,
          SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 1 THEN 1 ELSE 0 END) AS Q1,
          SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 2 THEN 1 ELSE 0 END) AS Q2,
          SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 3 THEN 1 ELSE 0 END) AS Q3,
          SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 4 THEN 1 ELSE 0 END) AS Q4
FROM 
          `etl-gb-poc.hresources.hired_employees` e
INNER JOIN 
          `etl-gb-poc.hresources.departments` d ON e.department_id = d.department_id
INNER JOIN 
          `etl-gb-poc.hresources.jobs` j ON e.job_id = j.job_id
WHERE     EXTRACT(YEAR FROM CAST(e.hire_date AS TIMESTAMP)) = 2021
GROUP BY d.department_name, j.job_title

---------------------------------------------------------------------------
-- View for Report 2 (Departments above the average)
CREATE OR REPLACE VIEW `etl-gb-poc.hresources.vw_departaments_top_2021` AS
WITH hiring_by_department AS (
    SELECT 
        d.department_id AS id_departament,
        d.department_name AS name_departament,
        COUNT(e.employee_id) AS total_hired
    FROM 
        `etl-gb-poc.hresources.departments` d
    INNER JOIN 
        `etl-gb-poc.hresources.hired_employees` e ON e.department_id = d.department_id
    WHERE 
        EXTRACT(YEAR FROM CAST(e.hire_date AS TIMESTAMP)) = 2021
    GROUP BY 
        d.department_id, d.department_name
)
SELECT 
    id_departament AS id,
    name_departament AS name,
    total_hired AS hired
FROM 
    hiring_by_department
WHERE 
    total_hired > (SELECT AVG(total_hired) FROM hiring_by_department)
