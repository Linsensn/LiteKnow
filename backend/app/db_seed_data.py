# backend/db_seed_data.py
# 专门用来存放初始化数据的模块


# ----------------------------
# 1. 用户数据 (users)
# ----------------------------
SEED_USERS = [
    {
        "wechat_openid": "wx_o001",
        "nickname": "学海无涯",
        "avatar_url": "https://avatar.test/1.png",
        "signature": "学而不思则罔",
        "created_at": "2026-07-06 09:00:00",
        "updated_at": "2026-07-06 09:00:00"
    },
    {
        "wechat_openid": "wx_o002",
        "nickname": "物理小王子",
        "avatar_url": "https://avatar.test/2.png",
        "signature": "探索宇宙的奥秘",
        "created_at": "2026-07-06 09:05:00",
        "updated_at": "2026-07-06 09:05:00"
    },
    {
        "wechat_openid": "wx_o003",
        "nickname": "英语语法侠",
        "avatar_url": "https://avatar.test/3.png",
        "signature": "Just do it.",
        "created_at": "2026-07-06 09:10:00",
        "updated_at": "2026-07-06 09:10:00"
    },
    {
        "wechat_openid": "wx_o004",
        "nickname": "数学王老师",
        "avatar_url": "https://avatar.test/4.png",
        "signature": "授人以鱼不如授人以渔",
        "created_at": "2026-07-06 09:15:00",
        "updated_at": "2026-07-06 09:15:00"
    }
]


# ----------------------------
# 2. 题库数据 (question_banks)
# ----------------------------
SEED_QUESTION_BANKS = [
    {
        "user_id": 1,
        "bank_name": "中考历史强化训练",
        "description": "涵盖近三年真题",
        "total_questions": 3,
        "created_at": "2026-07-06 10:00:00",
        "updated_at": "2026-07-06 10:00:00"
    },
    {
        "user_id": 2,
        "bank_name": "高中物理力学进阶",
        "description": "主要包含牛顿定律部分",
        "total_questions": 3,
        "created_at": "2026-07-06 10:05:00",
        "updated_at": "2026-07-06 10:05:00"
    },
    {
        "user_id": 3,
        "bank_name": "英语核心词汇与语法",
        "description": "高频错题汇总",
        "total_questions": 4,
        "created_at": "2026-07-06 10:10:00",
        "updated_at": "2026-07-06 10:10:00"
    }
]


# ----------------------------
# 3. 题目数据 (bank_questions)
# ----------------------------
SEED_BANK_QUESTIONS = [
    {
        "bank_id": 1,
        "chapter_name": "古代史",
        "question_type": "single_choice",
        "difficulty_level": "easy",
        "content": "隋朝大运河中心是？",
        "options_json": ["A. 洛阳", "B. 长安", "C. 余杭", "D. 北京"],
        "correct_answer": "A",
        "ai_analysis": "隋唐大运河以洛阳为中心。",
        "my_analysis": "别记成西安了！",
        "created_at": "2026-07-06 11:00:00",
        "updated_at": "2026-07-06 11:00:00"
    },
    {
        "bank_id": 1,
        "chapter_name": "近代史",
        "question_type": "single_choice",
        "difficulty_level": "medium",
        "content": "鸦片战争爆发于哪一年？",
        "options_json": ["A. 1840", "B. 1842", "C. 1856", "D. 1860"],
        "correct_answer": "A",
        "ai_analysis": "1840年英国发动鸦片战争。",
        "my_analysis": None,
        "created_at": "2026-07-06 11:05:00",
        "updated_at": "2026-07-06 11:05:00"
    },
    {
        "bank_id": 2,
        "chapter_name": "受力分析",
        "question_type": "single_choice",
        "difficulty_level": "hard",
        "content": "物体处于平衡状态，受力正确的是？",
        "options_json": ["A. 受力不为零", "B. 合力为零", "C. 必须静止", "D. 加速度不为零"],
        "correct_answer": "B",
        "ai_analysis": "平衡状态意味着合外力为零。",
        "my_analysis": "匀速直线运动也是平衡状态！",
        "created_at": "2026-07-06 11:10:00",
        "updated_at": "2026-07-06 11:10:00"
    },
    {
        "bank_id": 3,
        "chapter_name": "语法",
        "question_type": "single_choice",
        "difficulty_level": "medium",
        "content": "He _____ to school yesterday.",
        "options_json": ["A. go", "B. goes", "C. went", "D. going"],
        "correct_answer": "C",
        "ai_analysis": "yesterday 提示过去时态。",
        "my_analysis": None,
        "created_at": "2026-07-06 11:15:00",
        "updated_at": "2026-07-06 11:15:00"
    },
    {
        "bank_id": 3,
        "chapter_name": "集合与逻辑",
        "question_type": "single_choice",
        "difficulty_level": "easy",
        "content": "集合 A={1, 2}, B={2, 3}, 则 A∩B 等于？",
        "options_json": ["{1}", "{2}", "{1, 2, 3}", "{2, 3}"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】交集为两个集合的公共元素，即{2}。",
        "my_analysis": None,
        "created_at": "2026-07-06 16:00:00",
        "updated_at": "2026-07-06 16:00:00"
    },
    {
        "bank_id": 3,
        "chapter_name": "平面几何",
        "question_type": "single_choice",
        "difficulty_level": "medium",
        "content": "圆心在原点，半径为 2 的圆方程是？",
        "options_json": ["x²+y²=2", "x²+y²=4", "x+y=2", "x²+y²=1"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】圆的标准方程为x²+y²=r²，半径r=2，所以r²=4。",
        "my_analysis": "圆方程，半径要记得平方！",
        "created_at": "2026-07-06 16:05:00",
        "updated_at": "2026-07-06 16:05:00"
    },
    {
        "bank_id": 3,
        "chapter_name": "函数",
        "question_type": "single_choice",
        "difficulty_level": "hard",
        "content": "函数 f(x) = |x-1| 的对称轴是？",
        "options_json": ["x=0", "x=1", "y=1", "x=-1"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】绝对值函数 f(x)=|x-a| 关于 x=a 对称。",
        "my_analysis": "图像法最直观，看V型图的折点。",
        "created_at": "2026-07-06 16:10:00",
        "updated_at": "2026-07-06 16:10:00"
    },
    {
        "bank_id": 2,
        "chapter_name": "元素周期表",
        "question_type": "single_choice",
        "difficulty_level": "easy",
        "content": "下列元素中非金属性最强的是？",
        "options_json": ["Na", "Mg", "O", "F"],
        "correct_answer": "D",
        "ai_analysis": "【AI解析】同周期从左到右非金属性增强，F是元素周期表中非金属性最强的元素。",
        "my_analysis": None,
        "created_at": "2026-07-06 16:15:00",
        "updated_at": "2026-07-06 16:15:00"
    },
    {
        "bank_id": 2,
        "chapter_name": "化学反应速率",
        "question_type": "multiple_choice",
        "difficulty_level": "medium",
        "content": "（多选）下列能加快化学反应速率的是？",
        "options_json": ["A. 升高温度", "B. 使用催化剂", "C. 增大压强(气体)", "D. 降低温度"],
        "correct_answer": "ABC",
        "ai_analysis": "【AI解析】升高温度、增大压强（针对气体）、使用催化剂都能有效加快反应速率。",
        "my_analysis": "降低温度通常会减慢速率，排除D。",
        "created_at": "2026-07-06 16:20:00",
        "updated_at": "2026-07-06 16:20:00"
    },
    {
        "bank_id": 2,
        "chapter_name": "氧化还原",
        "question_type": "single_choice",
        "difficulty_level": "hard",
        "content": "在反应 2Na + Cl2 = 2NaCl 中，还原剂是？",
        "options_json": ["A. Na", "B. Cl2", "C. NaCl", "D. 电子"],
        "correct_answer": "A",
        "ai_analysis": "【AI解析】化合价升高被氧化的物质是还原剂，Na从0价升到+1价，故Na是还原剂。",
        "my_analysis": "失电子者为还原剂，记住“失升氧，得降还”。",
        "created_at": "2026-07-06 16:25:00",
        "updated_at": "2026-07-06 16:25:00"
    },
    {
        "bank_id": 1,
        "chapter_name": "细胞代谢",
        "question_type": "single_choice",
        "difficulty_level": "medium",
        "content": "光合作用产生 O2 的阶段是？",
        "options_json": ["A. 暗反应", "B. 光反应", "C. 有氧呼吸", "D. 无氧呼吸"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】光合作用的光反应阶段在类囊体薄膜上进行，主要发生水的光解产生O2。",
        "my_analysis": None,
        "created_at": "2026-07-06 16:30:00",
        "updated_at": "2026-07-06 16:30:00"
    },
    {
        "bank_id": 1,
        "chapter_name": "遗传规律",
        "question_type": "single_choice",
        "difficulty_level": "hard",
        "content": "纯合高茎(DD)与纯合矮茎(dd)杂交，F1的表现型是？",
        "options_json": ["A. DD", "B. dd", "C. 高茎", "D. 矮茎"],
        "correct_answer": "C",
        "ai_analysis": "【AI解析】F1基因型为Dd，表现为显性性状高茎。",
        "my_analysis": "表现型问的是外表，写DD/dd是基因型，别填错了！",
        "created_at": "2026-07-06 16:35:00",
        "updated_at": "2026-07-06 16:35:00"
    },
    {
        "bank_id": 1,
        "chapter_name": "细胞结构",
        "question_type": "multiple_choice",
        "difficulty_level": "medium",
        "content": "（多选）属于植物细胞特有结构的是？",
        "options_json": ["A. 细胞壁", "B. 叶绿体", "C. 液泡", "D. 线粒体"],
        "correct_answer": "ABC",
        "ai_analysis": "【AI解析】线粒体是动植物共有的。植物细胞特有细胞壁、叶绿体和液泡。",
        "my_analysis": "线粒体是能量工厂，动植物都要有！",
        "created_at": "2026-07-06 16:40:00",
        "updated_at": "2026-07-06 16:40:00"
    },
    {
        "bank_id": 2,
        "chapter_name": "电磁感应",
        "question_type": "single_choice",
        "difficulty_level": "hard",
        "content": "闭合电路在磁场中做切割磁感线运动时，产生感应电流的条件是？",
        "options_json": ["A. 只要做运动", "B. 只要在磁场中", "C. 穿过回路的磁通量发生变化", "D. 电路必须闭合"],
        "correct_answer": "C",
        "ai_analysis": "【AI解析】产生感应电流的根本条件是穿过闭合电路的磁通量发生变化。",
        "my_analysis": "磁通量变化是核心！",
        "created_at": "2026-07-06 16:45:00",
        "updated_at": "2026-07-06 16:45:00"
    },
    {
        "bank_id": 2,
        "chapter_name": "光学",
        "question_type": "single_choice",
        "difficulty_level": "easy",
        "content": "光在真空中传播速度约为？",
        "options_json": ["A. 3.0×10^5 m/s", "B. 3.0×10^8 m/s", "C. 3.0×10^8 km/s", "D. 3.0×10^6 m/s"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】真空光速 c ≈ 3.0×10^8 m/s。",
        "my_analysis": "单位一定要看清，是m/s还是km/s！",
        "created_at": "2026-07-06 16:50:00",
        "updated_at": "2026-07-06 16:50:00"
    },
    {
        "bank_id": 3,
        "chapter_name": "定语从句",
        "question_type": "single_choice",
        "difficulty_level": "medium",
        "content": "The book _____ I bought yesterday is very interesting.",
        "options_json": ["A. where", "B. which", "C. when", "D. who"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】先行词为 book（物），关系代词应使用 which 或 that。",
        "my_analysis": "物选which，人选who，地点选where。",
        "created_at": "2026-07-06 16:55:00",
        "updated_at": "2026-07-06 16:55:00"
    },
    {
        "bank_id": 3,
        "chapter_name": "被动语态",
        "question_type": "single_choice",
        "difficulty_level": "medium",
        "content": "The house _____ two years ago.",
        "options_json": ["A. is built", "B. was built", "C. has built", "D. builds"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】表示过去发生的动作且为被动含义，用一般过去时的被动语态 was built。",
        "my_analysis": None,
        "created_at": "2026-07-06 17:00:00",
        "updated_at": "2026-07-06 17:00:00"
    },
    {
        "bank_id": 3,
        "chapter_name": "非谓语动词",
        "question_type": "single_choice",
        "difficulty_level": "hard",
        "content": "_____ the teacher, the students stopped talking.",
        "options_json": ["A. Seeing", "B. Seen", "C. To see", "D. Saw"],
        "correct_answer": "A",
        "ai_analysis": "【AI解析】现在分词短语作状语，表示主动且发生在主要动作之前，用 Seeing。",
        "my_analysis": "做题技巧：如果主语是学生，主动看老师，选ing。",
        "created_at": "2026-07-06 17:05:00",
        "updated_at": "2026-07-06 17:05:00"
    },
    {
        "bank_id": 2,
        "chapter_name": "电功率",
        "question_type": "single_choice",
        "difficulty_level": "medium",
        "content": "一台电动机功率为 1kW，工作 2 小时，消耗电能为？",
        "options_json": ["A. 1 kWh", "B. 2 kWh", "C. 0.5 kWh", "D. 3 kWh"],
        "correct_answer": "B",
        "ai_analysis": "【AI解析】电能 W = Pt = 1kW × 2h = 2 kWh (度)。",
        "my_analysis": "基础计算题，别把单位弄混了。",
        "created_at": "2026-07-06 17:10:00",
        "updated_at": "2026-07-06 17:10:00"
    }
]


# ----------------------------
# 4. 会话数据 (sessions)
# ----------------------------
SEED_SESSIONS = [
    {
        "user_id": 1,
        "title": "历史考前冲刺",
        "task_type": "测验",
        "created_at": "2026-07-06 12:00:00",
        "updated_at": "2026-07-06 12:00:00"
    },
    {
        "user_id": 2,
        "title": "物理作业解答",
        "task_type": "精讲",
        "created_at": "2026-07-06 12:05:00",
        "updated_at": "2026-07-06 12:05:00"
    },
    {
        "user_id": 3,
        "title": "英语四级语法复习",
        "task_type": "摘要",
        "created_at": "2026-07-06 12:10:00",
        "updated_at": "2026-07-06 12:10:00"
    }
]


# ----------------------------
# 5. 消息数据 (messages)
# ----------------------------
SEED_MESSAGES = [
    {
        "session_id": 1,
        "role": "user",
        "content_type": "text",
        "content": "我想练习中考历史题。",
        "created_at": "2026-07-06 12:01:00",
        "updated_at": "2026-07-06 12:01:00"
    },
    {
        "session_id": 1,
        "role": "assistant",
        "content_type": "text",
        "content": "没问题，已为你加载中考历史题库。",
        "created_at": "2026-07-06 12:01:10",
        "updated_at": "2026-07-06 12:01:10"
    },
    {
        "session_id": 2,
        "role": "user",
        "content_type": "text",
        "content": "这道力学题怎么做？",
        "created_at": "2026-07-06 12:06:00",
        "updated_at": "2026-07-06 12:06:00"
    }
]


# ----------------------------
# 6. 附件数据 (attachments)
# ----------------------------
SEED_ATTACHMENTS = [
    {
        "user_id": 1,
        "message_id": 1,
        "file_type": "image/png",
        "file_url": "https://test.oss/q1.png",
        "extracted_text": "隋朝大运河...",
        "created_at": "2026-07-06 12:02:00",
        "updated_at": "2026-07-06 12:02:00"
    },
    {
        "user_id": 2,
        "message_id": 3,
        "file_type": "image/jpg",
        "file_url": "https://test.oss/p1.jpg",
        "extracted_text": "关于受力分析...",
        "created_at": "2026-07-06 12:07:00",
        "updated_at": "2026-07-06 12:07:00"
    },
    {
        "user_id": 3,
        "message_id": None,
        "file_type": "application/pdf",
        "file_url": "https://test.oss/g.pdf",
        "extracted_text": "Grammar guide...",
        "created_at": "2026-07-06 12:12:00",
        "updated_at": "2026-07-06 12:12:00"
    }
]


# ----------------------------
# 7. 错题本数据 (wrong_questions)
# ----------------------------
SEED_WRONG_QUESTIONS = [
    {
        "user_id": 2,
        "question_content": "关于惯性，下列说法正确的是？",
        "source_image_url": None,
        "user_answer": "B",
        "correct_answer": "C",
        "ai_analysis": "【AI解析】惯性大小仅与质量有关，与速度无关。",
        "my_analysis": "总是把惯性和运动状态搞混，记住：质量是惯性唯一量度！",
        "created_at": "2026-07-06 17:20:00",
        "updated_at": "2026-07-06 17:20:00"
    },
    {
        "user_id": 3,
        "question_content": "已知函数 f(x) = x^3 - 3x，求该函数在区间 [-2, 2] 上的最大值。",
        "source_image_url": "https://test.oss/math_err.jpg",
        "user_answer": "C",
        "correct_answer": "A",
        "ai_analysis": "【AI解析】应比较驻点和端点的函数值，f(2)=2。",
        "my_analysis": "只算了驻点，忘了比对端点值，这是导数题的大忌！",
        "created_at": "2026-07-06 17:25:00",
        "updated_at": "2026-07-06 17:25:00"
    },
    {
        "user_id": 2,
        "question_content": "闭合电路在磁场中做切割磁感线运动时，产生感应电流的条件是？",
        "source_image_url": None,
        "user_answer": "A",
        "correct_answer": "C",
        "ai_analysis": "【AI解析】必须穿过闭合电路的磁通量发生变化。",
        "my_analysis": "以为有运动就行，忘了还要磁通量变化这个大前提。",
        "created_at": "2026-07-06 17:30:00",
        "updated_at": "2026-07-06 17:30:00"
    }
]


# ----------------------------
# 8. 收藏夹数据 (favorites)
# ----------------------------
SEED_FAVORITES = [
    {
        "user_id": 3,
        "content_type": "英语语法",
        "cover_image_url": None,
        "content_data": {
            "title": "虚拟语气固定搭配",
            "content": "If I were you (如果我是你)，无论主语单复数。"
        },
        "source_session": 3,
        "created_at": "2026-07-06 17:40:00",
        "updated_at": "2026-07-06 17:40:00"
    },
    {
        "user_id": 3,
        "content_type": "数学技巧",
        "cover_image_url": None,
        "content_data": {
            "title": "导数单调性解题流程",
            "content": "1. 求定义域; 2. 求导; 3. 令导数等于0; 4. 列表分析"
        },
        "source_session": 3,
        "created_at": "2026-07-06 17:45:00",
        "updated_at": "2026-07-06 17:45:00"
    },
    {
        "user_id": 3,
        "content_type": "英语考点",
        "cover_image_url": "https://test.oss/grammar.png",
        "content_data": {
            "title": "非谓语动词做状语",
            "content": "主动用doing，被动用done，原因状语提前看。"
        },
        "source_session": 3,
        "created_at": "2026-07-06 17:50:00",
        "updated_at": "2026-07-06 17:50:00"
    }
]


# ----------------------------
# 9. 练习会话 (practice_sessions)
# ----------------------------
SEED_PRACTICE_SESSIONS = [
    {
        "user_id": 1,
        "bank_id": 1,
        "practice_mode": "sequential",
        "question_sequence": [1, 2],
        "last_viewed_index": 0,
        "status": "in_progress",
        "created_at": "2026-07-06 13:00:00",
        "updated_at": "2026-07-06 13:00:00"
    },
    {
        "user_id": 2,
        "bank_id": 2,
        "practice_mode": "random",
        "question_sequence": [3],
        "last_viewed_index": 0,
        "status": "completed",
        "created_at": "2026-07-06 13:05:00",
        "updated_at": "2026-07-06 13:05:00"
    },
    {
        "user_id": 3,
        "bank_id": 3,
        "practice_mode": "sequential",
        "question_sequence": [4],
        "last_viewed_index": 0,
        "status": "completed",
        "created_at": "2026-07-06 13:10:00",
        "updated_at": "2026-07-06 13:10:00"
    }
]


# ----------------------------
# 10. 练习记录 (practice_records)
# ----------------------------
SEED_PRACTICE_RECORDS = [
    {
        "session_id": 1,
        "user_id": 1,
        "question_id": 1,
        "is_completed": 1,
        "is_correct": 1,
        "user_answer": "A",
        "created_at": "2026-07-06 13:01:00",
        "updated_at": "2026-07-06 13:01:00"
    },
    {
        "session_id": 2,
        "user_id": 2,
        "question_id": 3,
        "is_completed": 1,
        "is_correct": 1,
        "user_answer": "B",
        "created_at": "2026-07-06 13:06:00",
        "updated_at": "2026-07-06 13:06:00"
    },
    {
        "session_id": 3,
        "user_id": 3,
        "question_id": 4,
        "is_completed": 1,
        "is_correct": 1,
        "user_answer": "C",
        "created_at": "2026-07-06 13:11:00",
        "updated_at": "2026-07-06 13:11:00"
    }
]
