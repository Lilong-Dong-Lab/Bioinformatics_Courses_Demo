```sql
-- 患者表
CREATE TABLE Patients (
    patient_id INT PRIMARY KEY,
    name VARCHAR(100),
    birth_date DATE,
    ethnicity VARCHAR(50),
    family_history TEXT,
    created_at TIMESTAMP
);

-- 基因表
CREATE TABLE Genes (
    gene_id INT PRIMARY KEY,
    gene_symbol VARCHAR(20) UNIQUE,
    full_name VARCHAR(200),
    chromosome VARCHAR(10),
    start_position INT,
    end_position INT,
    omim_id VARCHAR(20)
);

-- 突变表
CREATE TABLE Variants (
    variant_id INT PRIMARY KEY,
    gene_id INT REFERENCES Genes(gene_id),
    dna_change VARCHAR(100),
    protein_change VARCHAR(100),
    db_snp_id VARCHAR(20),
    clinical_significance ENUM('致病性', '可能致病性', '意义未明', '可能良性', '良性'),
    evidence_level ENUM('非常强', '强', '中等', '支持性')
);

-- 患者突变关联表
CREATE TABLE Patient_Variants (
    id INT PRIMARY KEY,
    patient_id INT REFERENCES Patients(patient_id),
    variant_id INT REFERENCES Variants(variant_id),
    test_date DATE,
    testing_lab VARCHAR(100),
    report_text TEXT,
    UNIQUE(patient_id, variant_id)
);

-- 文献引用表
CREATE TABLE Literature (
    reference_id INT PRIMARY KEY,
    pmid VARCHAR(20) UNIQUE,
    title TEXT,
    authors TEXT,
    journal VARCHAR(200),
    publication_date DATE,
    abstract TEXT
);

-- 突变证据关联表
CREATE TABLE Variant_Evidence (
    id INT PRIMARY KEY,
    variant_id INT REFERENCES Variants(variant_id),
    reference_id INT REFERENCES Literature(reference_id),
    evidence_type ENUM('功能性', '病例对照', '分离分析', '计算预测'),
    relevance_score INT(1-5)
);
```