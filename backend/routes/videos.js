import express from 'express';
import pool from '../db.js';

const router = express.Router();

// Get all videos
router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM movies');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get by name
router.get('/name/:name', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM movies WHERE LOWER(title) LIKE LOWER($1)', [`%${req.params.name}%`]);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get by genre
router.get('/genre/:genre', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM movies WHERE LOWER(category) = LOWER($1)', [req.params.genre]);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get by type (show, movie, etc.)
router.get('/type/:type', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM movies WHERE LOWER(category) = LOWER($1)', [req.params.type]);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get by topic (assuming topic is a column or tag)
router.get('/topic/:topic', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM movies WHERE LOWER(description) LIKE LOWER($1)', [`%${req.params.topic}%`]);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router; 