-- Needs still work, this is just the layout that we planned initially

DROP TABLE IF EXISTS websites;
CREATE TABLE IF NOT EXISTS websites (
    website_id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(512) NOT NULL,
    name VARCHAR(128) 
);


DROP TABLE IF EXISTS website_elements;
CREATE TABLE IF NOT EXISTS website_elements (
    element_id INT AUTO_INCREMENT PRIMARY KEY,
    website_id INT NOT NULL,
    parent_element_id INT NULL,
    dom_class VARCHAR(256),
    dom_id VARCHAR(256),
    dom_element VARCHAR(32),
    FOREIGN KEY (website_id) REFERENCES websites(website_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_element_id) REFERENCES website_elements(element_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS element_data;
CREATE TABLE IF NOT EXISTS data (
    data_id INT AUTO_INCREMENT PRIMARY KEY,
    website_id INT NOT NULL,
    value INT,
    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (website_id) REFERENCES websites(website_id) ON DELETE CASCADE
);
