import React, { useState } from "react";
import axios from "axios";
import {
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Box,
  Paper,
} from "@mui/material";
import { styled } from "@mui/system";

const BackgroundContainer = styled(Container)({
  background: "linear-gradient(to right, #141e30, #243b55)",
  minHeight: "100vh",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  flexDirection: "column",
  padding: "20px",
});

const StyledCard = styled(Card)({
  background: "rgba(255, 255, 255, 0.2)",
  backdropFilter: "blur(10px)",
  borderRadius: "10px",
  color: "white",
  width: "100%",
  maxWidth: "600px",
});

function App() {
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [downloadLink, setDownloadLink] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData);
      setUploadMessage(response.data.message);
      setDownloadLink(response.data.download_url);
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadMessage("File upload failed.");
    }
  };

  const handleAsk = async () => {
    if (!question) {
      alert("Please enter a question first.");
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:5000/ask", { question });

      if (response.data && response.data.answer) {
        const newMessage = { question, answer: response.data.answer };
        setChatHistory([...chatHistory, newMessage]);
        setAnswer(response.data.answer);
      } else {
        setAnswer("AI did not return a response.");
      }

      setQuestion(""); // Clear input after asking
    } catch (error) {
      console.error("Error getting AI response:", error);
      setAnswer("Error: AI service is unavailable.");
    }
  };

  return (
    <BackgroundContainer>
      <Typography variant="h3" align="center" gutterBottom color="white">
        Financial Statement Analyzer
      </Typography>

      <StyledCard sx={{ padding: 3, marginBottom: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Upload PDF File
          </Typography>
          <input type="file" onChange={handleFileChange} style={{ marginBottom: "10px" }} />
          <Button variant="contained" color="primary" onClick={handleUpload}>
            Upload & Process
          </Button>
          <Typography variant="body1" color="white" mt={2}>
            {uploadMessage}
          </Typography>
          {downloadLink && (
            <Button
              variant="contained" color="success"
              href={`http://127.0.0.1:5000${downloadLink}`}
              download
              sx={{ marginTop: 2 }}
            >
              Download Processed Excel File
            </Button>
          )}
        </CardContent>
      </StyledCard>

      <StyledCard sx={{ padding: 3, marginBottom: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            AI Co-Pilot (Ask Anything!)
          </Typography>
          <Paper
            elevation={3}
            sx={{
              maxHeight: 250,
              overflowY: "auto",
              padding: 2,
              backgroundColor: "#1e293b",
              borderRadius: 2,
              marginBottom: 2,
            }}
          >
            {chatHistory.length === 0 ? (
              <Typography variant="body2" color="white">
                No conversation yet. Ask a question!
              </Typography>
            ) : (
              chatHistory.map((msg, index) => (
                <Box key={index} sx={{ marginBottom: 1 }}>
                  <Typography variant="body2">
                    <strong>You:</strong> {msg.question}
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#38bdf8" }}>
                    <strong>AI:</strong> {msg.answer}
                  </Typography>
                </Box>
              ))
            )}
          </Paper>
          <TextField
            fullWidth
            label="Ask AI about your financial data..."
            variant="outlined"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            sx={{ marginTop: 2, backgroundColor: "white" }}
          />
          <Button variant="contained" color="success" onClick={handleAsk} sx={{ marginTop: 2 }}>
            Ask AI
          </Button>
        </CardContent>
      </StyledCard>
    </BackgroundContainer>
  );
}

export default App;
