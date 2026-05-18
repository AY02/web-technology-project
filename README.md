# web-technology-project
A simple web app for note-taking and to-do lists designed to boost students’ productivity. The web app was developed as part of the web technologies course.

---

In Django version 6.0.5, the admin cannot register models with composite primary keys. Consequently, we have implemented the ProjectPermission model with a separate identifier and have placed a constraint on the uniqueness of the (user_id, project_id) pair, even though the primary key could actually have been (user_id, project_id), as a user cannot have multiple roles on the same project.