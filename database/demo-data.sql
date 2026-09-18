-- Insert Generic Webpages
INSERT INTO webpages (url, page_name, run_time, is_enabled) VALUES
('https://example.com/page1', 'Website 1', '01:00:00', FALSE), -- webpage_id: 1 (Healthy)
('https://example.com/page2', 'Website 2', '02:00:00', FALSE), -- webpage_id: 2 (Has bad locators)
('https://example.com/page3', 'Website 3', '03:00:00', FALSE); -- webpage_id: 3 (Failing page load)

-- Insert Generic Target Elements
INSERT INTO elements (webpage_id, locator, metric_name) VALUES
(1, '#element-1A', 'Metric 1A'), -- element_id: 1
(1, '#element-1B', 'Metric 1B'), -- element_id: 2
(2, '#element-2A', 'Metric 2A'), -- element_id: 3 (Valid)
(2, '#element-2B', 'Metric 2B'), -- element_id: 4 (Value parse error)
(2, '#element-2C', 'Metric 2C'); -- element_id: 5 (Locator missing)

-- Insert Scraped Data (Only successful elements get inserted via _persist_element_data)
INSERT INTO element_data (element_id, value, created_at) VALUES
-- Day 1 Runs
(1, 100.00, NOW() - INTERVAL 1 DAY),
(2, 25.50,  NOW() - INTERVAL 1 DAY),
(3, 500.00, NOW() - INTERVAL 1 DAY),

-- Day 0 (Today's Runs)
(1, 105.00, NOW()),
(2, 26.00,  NOW()),
(3, 512.50, NOW());

-- Insert Webpage Logs
-- Mirrors _initialize_webpage_log & _finalize_webpage_log
INSERT INTO webpage_logs (webpage_log_id, webpage_id, attempted_at, status, message) VALUES
-- Run 1: Website 1 (Fully successful yesterday)
(1, 1, NOW() - INTERVAL 1 DAY, 'success', 'Scraped successfully'),

-- Run 2: Website 2 (Partial failure yesterday - invalid value and missing element)
(2, 2, NOW() - INTERVAL 1 DAY, 'partial', 'ValueError for element 4\nElementNotFoundError for element 5'),

-- Run 3: Website 3 (Page load crash today - note early return behavior)
(3, 3, NOW(), 'failure', 'Page load failed: Timeout 30000ms exceeded while waiting for page to load'),

-- Run 4: Website 1 (Fully successful today)
(4, 1, NOW(), 'success', 'Scraped successfully'),

-- Run 5: Website 2 (Partial failure today - elements 4 & 5 failing)
(5, 2, NOW(), 'partial', 'ValueError for element 4\nElementNotFoundError for element 5');

-- Insert Element Logs
-- Mirrors _insert_element_log calls within _run_scrapes_by_webpage
INSERT INTO element_logs (webpage_log_id, element_id, attempted_at, status, message) VALUES
-- Logs for webpage_log_id 1 (Website 1 - Yesterday)
(1, 1, NOW() - INTERVAL 1 DAY, 'success', 'Scraped successfully'),
(1, 2, NOW() - INTERVAL 1 DAY, 'success', 'Scraped successfully'),

-- Logs for webpage_log_id 2 (Website 2 - Yesterday)
(2, 3, NOW() - INTERVAL 1 DAY, 'success', 'Scraped successfully'),
(2, 4, NOW() - INTERVAL 1 DAY, 'failure', 'Failed to convert "N/A" to Decimal: Invalid literal for Decimal: "N/A"'),
(2, 5, NOW() - INTERVAL 1 DAY, 'failure', 'ElementNotFoundError: Element with locator "#element-2C" was not found on page'),

-- Note: webpage_log_id 3 has NO element logs because scraper.load() threw an exception!

-- Logs for webpage_log_id 4 (Website 1 - Today)
(4, 1, NOW(), 'success', 'Scraped successfully'),
(4, 2, NOW(), 'success', 'Scraped successfully'),

-- Logs for webpage_log_id 5 (Website 2 - Today)
(5, 3, NOW(), 'success', 'Scraped successfully'),
(5, 4, NOW(), 'failure', 'Failed to convert "OUT OF STOCK" to Decimal: Invalid literal for Decimal: "OUT OF STOCK"'),
(5, 5, NOW(), 'failure', 'ElementNotFoundError: Element with locator "#element-2C" was not found on page');
