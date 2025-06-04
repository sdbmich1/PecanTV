import express from 'express';
import dotenv from 'dotenv';
import authRoutes from './routes/auth.js';
import videoRoutes from './routes/videos.js';

dotenv.config();

const app = express();
app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/videos', videoRoutes);

app.get('/', (req, res) => {
  res.send('PecanTV API is running');
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 