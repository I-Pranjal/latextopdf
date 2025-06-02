FROM python:3.10-slim

# Install LaTeX
RUN apt-get update && \
    apt-get install -y texlive-latex-base texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra && \
    apt-get clean
    
RUN pip install -r python-server/ /requirements.txt


WORKDIR /app
COPY python-server/ /app
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]
