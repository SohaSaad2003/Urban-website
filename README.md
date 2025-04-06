Sure! Here’s a clear and simple guide you can send to your friends on how to **clone**, **push**, and **pull** a private GitHub repository after being added as a collaborator:

---

## 🛠 Git Instructions for Collaborators

### ✅ Step 1: Accept the Invitation
First, go to your email or GitHub notifications and **accept the invitation** to collaborate on the repository.

---

### 📥 Step 2: Clone the Repository (once)
Use this command to download the project to your local machine:

```bash
git clone https://github.com/SohaSaad2003/Urban-website.git
```

Then move into the folder:

```bash
cd Urban-website
```

---

### 🔄 Step 3: Pull the Latest Code (before you start working)

Before making any changes, always pull the latest version of the project to make sure you're working on the most updated files:

```bash
git pull origin main  # or 'master' if that’s the branch name
```

---

### ✍️ Step 4: Make Your Changes

Edit files, add new ones, or do whatever work you need to do.

---

### ✅ Step 5: Add and Commit Your Changes

After finishing your edits:

```bash
git add .
git commit -m "Your message describing the changes"
```

---

### 🚀 Step 6: Push Your Changes to GitHub

```bash
git push origin main
```

---

### 🔁 Step 7: Repeat

- Always do `git pull origin main` before starting new work.
- Then follow steps 4 → 6.

---

### 💡 Notes

- If asked for a username/password during push/pull, make sure you're logged in to GitHub or using a Personal Access Token (PAT) if required.
- If you get an error about `main` not existing, check the branch name using:
  
  ```bash
  git branch
  ```

---

Let me know if you want this as a PDF or to send via WhatsApp or Messenger format! 😊
