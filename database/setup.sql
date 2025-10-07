-- Stores webpages to be scraped
CREATE TABLE IF NOT EXISTS webpages (
    webpage_id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(512) NOT NULL UNIQUE,
    page_name VARCHAR(128),
    run_minute TINYINT DEFAULT 0,
    run_hour TINYINT DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE
);

-- Defines scraping jobs linked to webpages and target elements
CREATE TABLE IF NOT EXISTS elements (
    element_id INT AUTO_INCREMENT PRIMARY KEY,
    webpage_id INT NOT NULL,
    locator VARCHAR(512) NOT NULL,
    metric_name VARCHAR(128),
    FOREIGN KEY (webpage_id) REFERENCES webpages(webpage_id) ON DELETE CASCADE,
    UNIQUE(webpage_id, locator)
);

-- Stores scraped data values over time
CREATE TABLE IF NOT EXISTS element_data (
    data_id INT AUTO_INCREMENT PRIMARY KEY,
    element_id INT NOT NULL,
    value DECIMAL(15,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (element_id) REFERENCES elements(element_id) ON DELETE CASCADE
);
