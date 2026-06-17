-- ============================================
-- 数据库初始化脚本 - aihumanproject
-- 创建时间: 2026-05-18
-- 说明: 基于示范景区公开资料包创建数据表
-- ============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS aihumanproject 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE aihumanproject;

-- ============================================
-- 表1: tourist_behavior_data (景点景区旅游数据行为分析数据)
-- 数据来源: 景点景区旅游数据行为分析数据.xlsx
-- 记录数: 140,447行
-- 用途: 游客行为分析、个性化推荐、运营决策支持
-- ============================================
DROP TABLE IF EXISTS tourist_behavior_data;

CREATE TABLE tourist_behavior_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    tourist_id VARCHAR(50) NOT NULL COMMENT '游客ID',
    user_nickname VARCHAR(100) COMMENT '用户昵称',
    age INT COMMENT '年龄',
    gender VARCHAR(10) COMMENT '性别',
    attraction_name VARCHAR(200) NOT NULL COMMENT '景点名称',
    attraction_content TEXT COMMENT '景点内容描述',
    attraction_type VARCHAR(100) COMMENT '景点类型',
    visit_date DATE COMMENT '游览日期',
    stay_duration DECIMAL(10,2) COMMENT '停留时长（分钟）',
    ticket_cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '门票消费（元）',
    food_cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '餐饮消费（元）',
    shopping_cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '购物消费（元）',
    transport_cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '交通消费（元）',
    entertainment_cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '娱乐消费（元）',
    total_cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '总消费（元）',
    group_size INT DEFAULT 1 COMMENT '同行人数',
    satisfaction INT COMMENT '满意度评分（1-5）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    
    -- 索引优化
    INDEX idx_tourist_id (tourist_id),
    INDEX idx_attraction_name (attraction_name),
    INDEX idx_visit_date (visit_date),
    INDEX idx_age (age),
    INDEX idx_satisfaction (satisfaction),
    INDEX idx_total_cost (total_cost)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='景点景区旅游数据行为分析表';


-- ============================================
-- 表2: attraction_details (景点详情)
-- 数据来源: 灵山胜境 景点结构化数据集.docx + 灵山胜境：历史、文化、景点特色与个性化游览指南.docx
-- 记录数: 约30个核心景点（灵山胜境17个 + 拈花湾13个）
-- 用途: RAG知识库、事实性问答、景点详情查询
-- ============================================
DROP TABLE IF EXISTS attraction_details;

CREATE TABLE attraction_details (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    scenic_area VARCHAR(100) NOT NULL COMMENT '景区名称（如：灵山胜境、拈花湾禅意小镇）',
    attraction_id VARCHAR(50) NOT NULL UNIQUE COMMENT '景点ID（如：LS-001）',
    attraction_name VARCHAR(200) NOT NULL COMMENT '景点名称',
    location VARCHAR(500) COMMENT '具体位置',
    building_params TEXT COMMENT '建筑/景观参数（尺寸、材质等）',
    core_function VARCHAR(500) COMMENT '核心功能',
    cultural_meaning TEXT COMMENT '文化内涵',
    detailed_description LONGTEXT COMMENT '详细介绍',
    highlights TEXT COMMENT '游玩亮点',
    performance_info VARCHAR(500) COMMENT '演艺/开放信息',
    attraction_type VARCHAR(100) COMMENT '景点类型',
    remarks TEXT COMMENT '备注',
    
    -- 扩展字段（从历史文化游览指南中提取）
    history_background TEXT COMMENT '历史背景',
    cultural_stories LONGTEXT COMMENT '文化故事/典故',
    recommended_routes TEXT COMMENT '推荐路线',
    photography_tips TEXT COMMENT '摄影建议',
    family_friendly TINYINT(1) DEFAULT 0 COMMENT '是否适合亲子游（0-否，1-是）',
    photo_spot TINYINT(1) DEFAULT 0 COMMENT '是否为拍照打卡点（0-否，1-是）',
    
    -- 元数据
    data_source VARCHAR(200) COMMENT '数据来源文件',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引优化
    INDEX idx_attraction_id (attraction_id),
    INDEX idx_attraction_name (attraction_name),
    INDEX idx_scenic_area (scenic_area),
    INDEX idx_attraction_type (attraction_type),
    FULLTEXT INDEX ft_description (detailed_description, cultural_meaning, history_background)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='景点详情表（RAG知识库）';


-- ============================================
-- 说明：其他表保持不变
-- ============================================
-- 以下表已在项目中定义，此处不再重复创建：
-- - conversations (对话记录)
-- - qa_items (问答对)
-- - documents (文档管理)
-- - visitor_feedback (游客反馈)
-- - dh_config (数字人配置)

-- 如需查看现有表结构，可执行：
-- SHOW TABLES;
-- DESCRIBE conversations;


-- ============================================
-- 可选：插入示例数据（用于测试）
-- ============================================

-- 示例1: 插入一条游客行为数据
INSERT INTO tourist_behavior_data 
(tourist_id, user_nickname, age, gender, attraction_name, attraction_content, attraction_type, 
 visit_date, stay_duration, ticket_cost, food_cost, shopping_cost, transport_cost, 
 entertainment_cost, total_cost, group_size, satisfaction)
VALUES 
('U00001', '上海解小秀', 32, '女', '宁波方特东方神画', '宁波方特东方神画：科技与文化交融的东方神话王国...', '主题乐园',
 '2025-10-01', 10.7, 280.00, 763.90, 759.58, 66.12, 476.35, 2345.95, 2, 3);

-- 示例2: 插入一个景点详情
INSERT INTO attraction_details
(scenic_area, attraction_id, attraction_name, location, building_params, core_function, 
 cultural_meaning, detailed_description, highlights, performance_info, attraction_type)
VALUES 
('灵山胜境', 'LS-001', '灵山大照壁', '景区入口处，面朝太湖，背靠景区核心区域', 
 '长39.8m，高7m，采用优质青石雕刻而成，被誉为"华夏第一壁"', 
 '视觉屏障与景观节点，进入灵山胜境的第一道视觉冲击',
 '体现佛教文化的庄重与神圣，象征佛法无边的意境',
 '灵山大照壁是进入灵山胜境的第一道景观，整体造型恢弘大气，细节雕刻精美。照壁正面刻有"灵山胜境"四个大字，背面则是精美的佛教浮雕，展现了佛陀生平的重要场景。',
 '最佳拍摄角度：正面全景、侧面特写；建议光线：清晨或黄昏',
 '全天开放，免费参观', '标志性建筑');


-- ============================================
-- 验证表创建成功
-- ============================================
SHOW TABLES;

SELECT '✅ 数据库表创建完成！' AS status;
SELECT '📊 tourist_behavior_data: 游客行为数据表' AS table_info;
SELECT '📋 attraction_details: 景点详情表' AS table_info;
