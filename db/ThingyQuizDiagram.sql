CREATE TABLE `users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_oauth_token` varchar(255)
);

CREATE TABLE `quizzes` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `date` datetime,
  `difficulty` int unsigned,
  `quiz_type` varchar(255),
  `quiz_category` varchar(255)
);

CREATE TABLE `questions` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255)
);

CREATE TABLE `answers` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `question_id` int,
  `title` varchar(255),
  `is_correct` boolean 
);

CREATE TABLE `quiz_questions` (
  `quiz_id` int,
  `question_id` int,
  PRIMARY KEY (`question_id`, `quiz_id`)
);

CREATE TABLE `user_quizzes` (
  `user_id` int,
  `quiz_id` int,
  PRIMARY KEY (`user_id`, `quiz_id`)
);

CREATE TABLE `user_answers` (
  `user_id` int,
  `quiz_id` int,
  `answer_id` int,
  `answer_delay` int unsigned,
  PRIMARY KEY (`user_id`, `quiz_id`, `answer_id`)
);

ALTER TABLE `answers` ADD FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`);

ALTER TABLE `quiz_questions` ADD FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`);

ALTER TABLE `quiz_questions` ADD FOREIGN KEY (`quiz_id`) REFERENCES `quizzes` (`id`);

ALTER TABLE `user_quizzes` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `user_quizzes` ADD FOREIGN KEY (`quiz_id`) REFERENCES `quizzes` (`id`);

ALTER TABLE `user_answers` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `user_answers` ADD FOREIGN KEY (`quiz_id`) REFERENCES `quizzes` (`id`);

ALTER TABLE `user_answers` ADD FOREIGN KEY (`answer_id`) REFERENCES `answers` (`id`);

CREATE INDEX `questions_index_0` ON `questions` (`title`);
