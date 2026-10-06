OPEN BOOK — Asynchronous Programming
======================================================================
ใช้ทบทวนตั้งแต่พื้นฐานและค้นสูตรโค้ดระหว่างทำโจทย์
เอกสารฝึก ไม่ใช่ข้อสอบจริง และไม่มีข้อมูลยืนยันขอบเขตข้อสอบของอาจารย์

เริ่มอ่าน: 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11
ค้นเร็ว: 01_quick_index.txt
รวมเล่ม: 12_openbook_all.txt
ข้อสอบฝึก 30 ข้อพร้อมเฉลย: 13_practice_exam_with_answers.txt
00-REPOgithub.py เก็บต้นฉบับเดิมไว้ตามคำขอ

ไฟล์ทั้งหมดเป็น UTF-8 ไม่มี ANSI color และไม่มี Markdown renderer requirement
CODE เป็นตัวอย่างใหม่สำหรับฝึก; ภาคผนวกเป็นเนื้อหาเดิมแปลงรูปแบบ
Python ที่ใช้ตรวจ: 3.12; templates HTTP/FastAPI/Redis ต้องมี dependencies/server
ตัวอย่างใช้ localhost เป็นค่า template ไม่ได้ยืนยัน endpoint ของห้องเรียน

แหล่งต้นฉบับ: repo Boonyapat-12/async-2026-CDTI, commit ฐาน 058b3fe
โฟลเดอร์ Week1–10 และคู่มือรายสัปดาห์เป็นแหล่งเทียบพฤติกรรม
เอกสารทางการที่ตรวจเพื่อแก้จุดกำกวม:
https://docs.python.org/3/library/asyncio-task.html
https://docs.python.org/3/library/asyncio-queue.html
https://fastapi.tiangolo.com/async/
https://www.python-httpx.org/async/
https://redis.io/docs/latest/develop/pubsub/
https://redis.io/docs/latest/commands/xreadgroup/

รายการโค้ดอ้างอิงใน repo (ชื่อจริง ไม่ได้รันทุกไฟล์):
Week1/coffee01_synchronous.py : make_coffee, main
Week1/coffee02_thread.py : make_coffee, main
Week1/coffee03_multiprocess.py : make_coffee, main
Week1/coffee04_asyncio.py : make_coffee, main
Week1/pid01_synchronous.py : make_coffee, main
Week1/pid02_thread.py : make_coffee, main
Week1/pid03_multiprocess.py : make_coffee, main
Week1/pid04_asyncio.py : make_coffee, main
Week1/ps01_synchronous.py : make_coffee, main
Week1/ps02_thread.py : make_coffee, main
Week1/ps03_multiprocess.py : make_coffee, main
Week1/ps04_asyncio.py : make_coffee, main
Week1/up01_synchronous.py : log, update_cup_number, make_coffee, main
Week1/up02_thread.py : log, update_cup_number, make_coffee, main
Week1/up03_multiprocess.py : log, update_cup_number, make_coffee, main
Week1/up04_asyncio.py : log, update_cup_number, make_coffee, main
Week2/asyncio01.py : greet
Week2/asyncio02.py : greet
Week2/asyncio03.py : greet
Week2/asyncio04.py : main
Week2/asyncio05.py : serve_customer, main
Week2/asyncio06.py : cook_spaghetti, main
Week2/asyncio07.py : cook_spaghetti, main
Week2/asyncio08.py : kitchen_crew, bar_Crew, main
Week2/asyncio09.py : serve_customer, main
Week2/asyncio10.py : calculate_bill, main
Week2/restaurant_01_asyncio.py : greet_diners, customer_private_workflow, main
Week2/restaurant_01_multiprocess.py : greet_diners, customer_private_workflow
Week2/restaurant_01_simple.py : greet_diners, take_order, do_cooking, mini_bar, serve_customer, main
Week2/restaurant_01_thread.py : greet_diners, customer_private_workflow
Week3/smart_courier.py : delivery_task, main
Week3/stock_api.py : get_stock_price
Week3/stock_price.py : fetch_stock_price, main
Week3/stock_price_httpx.py : fetch_stock_price, main
Week3/task_01_status.py : short_job, main
Week3/task_02_exception.py : division_worker, main
Week3/task_03_cancel.py : background_loop, main
Week3/task_04_callback.py : alert_manager, download_file, main
Week3/task_05_nameing.py : background_worker, main
Week3/task_06_loop_introspection.py : dynamic_job, main
Week3/task_07_gather.py : fetch_db_record, main
Week3/task_08_wait.py : network_probe, main
Week3/task_09_wait_for.py : long_query_simulation, main
Week3/task_10_gather_vs_wait.py : runner, main
Week4/food_utils.py : send_order_to_kitchen
Week4/foodcourt_01_create_task.py : main
Week4/foodcourt_02_gather.py : main
Week4/foodcourt_03_wait_first.py : main
Week4/foodcourt_04_wait_for.py : main
Week4/foodcourt_05_mix_concepts.py : main
Week4/foodcourt_api.py : cook_food
Week4/light/light_01.py : main
Week4/light/light_02.py : main
Week4/light/light_utils.py : get_all_lights, set_light, set_lights_concurrently, reset_all_lights, cleanup_lights
Week5/chat-hello/client.py : get_index
Week5/chat-hello/client2.py : get_index
Week5/chat-hello/main.py : get_status, websocket_endpoint, __init__, connect, disconnect, broadcast
Week5/fastapi_async_basic_lab.py : sync_delay, async_delay, run_concurrent_tasks, fetch_data_from_api
Week5/fastapi_async_external_api_lab.py : fetch_single_api, fetch_sequentially, fetch_concurrently, fetch_safely
Week5/fastapi_basic_lab.py : read_root, read_item_by_id, search_users, register_student
Week5/rocket/dashboard.py : get_dashboard
Week5/rocket/main.py : websocket_endpoint, __init__, connect, disconnect, broadcast
Week5/rocket/student.py : get_index
Week5/rocket/student2.py : get_index
Week6/robots.py : reset_factory, grab_part, run_robot_task, main
Week7/client.py : hunt_coupons
Week7/client_example.py : hunt_coupons
Week7/server.py : claim_coupon, get_summary
Week7/server_example.py : reset_coupon_state, claim_coupon, get_my_coupons, get_summary
Week7/server_vulnerable.py : claim_coupon, get_summary
Week7/test_server_example.py : request, setUp, test_my_coupons_returns_only_requested_students_claims, test_my_coupons_rejects_unknown_student
Week8/01_synchronous_vs_asynchronous.py : sync_task, main_sync, async_task, main_async
Week8/02_basic_asyncio_queue.py : producer, consumer, main
Week8/03_put_and_get_mechanism.py : slow_producer, eager_consumer, main
Week8/04_bounded_queue_backpressure.py : fast_producer, slow_consumer, main
Week8/05_task_completion_and_join.py : worker, main
Week8/06_scraper_downloader.py : link_scraper, image_downloader, main
Week8/07_coupon_producer_consumer.py : producer, consumer, main
Week8/08_coupon_producer_consumer2.py : producer, consumer, main
Week9/dashboard_listener.py : generate_dashboard_ui, listen_to_dashboard
Week9/student1_telemetry_producer.py : wait_for_new_green_light, produce_f1_telemetry
Week9/student2_pit_strategy_engineer.py : init_group, pit_strategy_worker
Week9/student3_race_control_engine_safety.py : init_group, safety_alert_worker
Week9/student4_DRS_automation_controller.py : init_group, drs_controller_worker
Week9/student5_dashboard_broadcaster.py : init_group, dashboard_broadcaster_worker
Week9/teacher_race_control.py : reset_race_state, generate_race_ui, listen_to_pubsub, main
Week10/bot.py : __init__, send_action, listen_game_state, brain_loop, run
Week10/dashboard.py : __init__, clear_screen, render_board, run
Week10/server.py : __init__, init_game, reset_game, start_countdown, listen_commands, process_buffered_actions, update_bullets, check_winner_and_timer, wait_for_host_input, game_loop, run
Week10/tank.py : __init__, register, send_action, on_press, run
Week10/web_dashboard.py : redis_listener, lifespan, get, websocket_endpoint, __init__, connect, disconnect, broadcast


ข้อชี้แจงก่อนอ่านคู่มือและภาคผนวกเดิม
======================================================================
1. คำว่า await เป็นจุดที่อาจพัก ไม่ได้สลับ task ทุกครั้งเสมอ
2. FIRST_COMPLETED อาจมี done หลายตัว; ต้องจัดการทุก task ใน done
3. gather ค่าเริ่มต้นไม่ cancel พี่น้องเพราะ task หนึ่งเกิด exception
4. join รอ unfinished count; ไม่รับประกัน worker หยุดหรือธุรกิจสำเร็จ
5. Streams + group ต้องมี recovery และ idempotency; ไม่ได้ exactly-once อัตโนมัติ
6. Pub/Sub ไม่เก็บ history; Redis persistence ไม่ทำให้ Pub/Sub replay ได้
7. asyncio.Lock ไม่ประสานหลาย worker process
8. Tank server ใน repo ใช้ TICK_RATE=0.2 (เป้าหมาย 5 FPS) ไม่ใช่ 10 FPS
9. ตัวอย่างเดิมที่ cancel pending ควร await งานหลัง cancel ให้ cleanup เสร็จ
10. คำว่า parallel ในคอมเมนต์บางตัวอย่างหมายถึง concurrent ไม่ใช่หลาย core
