<h1 align="center">127.0.0.1 - Find Your Home 🏠</h1>
<p align="center">
	<a href="https://github.com/scp-2021-jan-cmpt-756/term-project-team-a" alt="Built with Swag">
		<img src="http://ForTheBadge.com/images/badges/built-with-swag.svg" />
	</a>
	<br>
<!-- 		<a href="https://github.com/scp-2021-jan-cmpt-756/term-project-team-a" alt="127.0.0.1 Repo Size">
			<img src="https://img.shields.io/github/repo-size/scp-2021-jan-cmpt-756/term-project-team-a" />
		</a> -->
	</p>

> Cloud based microservices POC for validating the robustness of Distributed Systems.


<p align="center">
	<a href="https://www.youtube.com/watch?v=ATlthWBY0pA" alt="Youtube Video">
        <img src="https://img.youtube.com/vi/ATlthWBY0pA/0.jpg" />
    </a>
	</p>


<p align="center">
	<a>
        <img src="/wiki/architecture.png" />
	</a>
</p>

## ✨ Demo

1. Make a copy of the `tpl-vars-blank.txt`and rename it as `tpl-vars.txt` in [cluster](IaC/cluster/) folder
2. Update the `tpl-vars.txt` with your aws credentials - [sample file](IaC/cluster/tpl-vars-blank.txt)
3. Go to the [IaC](IaC/) folder and run:
  ```sh
  make -f k8s-tpl.mak template
  make -f az.mak start
  make -f k8s.mak provision
  ```

Make sure to install `aws-cli`, `az-cli`, `kubectl` and `docker` before running the above commands.

## 🚀 Development Setup

Clone the repository:

```sh
git clone git@github.com:scp-2021-jan-cmpt-756/term-project-team-a.git
```

Install and setup the required tools mentioned above

That's it. You can now start contributing to the project.

## Code Contributors

Thanks to the following people who have contributed to this project:

- [@anuj](https://github.com/Anuj-Saboo) 📹 💻
- [@inderpartap](https://github.com/inderpartap) 📹 💻
- [@navaneeth](https://github.com/jediXNavi) 📹 💻
- [@rishabh](https://github.com/rja40) 📹 💻
- [@tavleen](https://github.com/tssahota) 📹 💻

## 🤝 Contributing

Contributions, issues and feature requests are welcome.<br /> Feel free to check
[issues page](https://github.com/scp-2021-jan-cmpt-756/term-project-team-a/issues) if you want to
contribute.<br /> To contribute to 127.0.0.1, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push --set-upstream origin <branch_name>`
5. Create the pull request.

Alternatively see the GitHub documentation on
[creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## Show your support

Please ⭐️ this repository if this project helped you!

---
