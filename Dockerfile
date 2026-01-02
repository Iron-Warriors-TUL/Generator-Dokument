# Start with a lightweight Python image
FROM python:3.13-slim

# 1. Install LaTeX and Polish language support
# We need 'latex-extra' for packages like geometry/eso-pic and 'lang-polish' for ą/ę support
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-lang-polish \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy python requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application
COPY . .

# 5. Ensure the output directory exists
RUN mkdir -p generated

# 6. Expose the port Flask runs on
EXPOSE 5000

# 7. Run the application
# We use host=0.0.0.0 so the container listens to the outside world
# RUN python create_user.py
CMD ["flask", "run", "--host=0.0.0.0"]