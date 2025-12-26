const { Pool } = require('pg');
require('dotenv').config();

async function testConnection() {
  console.log('\n=== Testing PostgreSQL Connection ===\n');

  console.log('Configuration:');
  console.log(`Host: ${process.env.DB_HOST || 'localhost'}`);
  console.log(`Port: ${process.env.DB_PORT || 5432}`);
  console.log(`Database: ${process.env.DB_NAME || 'hotel_restaurant_db'}`);
  console.log(`User: ${process.env.DB_USER || 'postgres'}`);
  console.log(`Password: ${process.env.DB_PASSWORD ? '***' + process.env.DB_PASSWORD.slice(-3) : '(empty)'}`);
  console.log('');

  const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'hotel_restaurant_db',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
  });

  try {
    console.log('Attempting to connect...');
    const client = await pool.connect();
    console.log('✅ Connection successful!');

    const result = await client.query('SELECT version()');
    console.log('\nPostgreSQL Version:');
    console.log(result.rows[0].version);

    // Check if database exists
    const dbCheck = await client.query(
      "SELECT datname FROM pg_database WHERE datname = $1",
      [process.env.DB_NAME || 'hotel_restaurant_db']
    );

    if (dbCheck.rows.length > 0) {
      console.log(`\n✅ Database '${process.env.DB_NAME || 'hotel_restaurant_db'}' exists`);
    } else {
      console.log(`\n❌ Database '${process.env.DB_NAME || 'hotel_restaurant_db'}' does NOT exist`);
      console.log('   Create it with: CREATE DATABASE hotel_restaurant_db;');
    }

    client.release();
    await pool.end();

    console.log('\n=== Connection Test Complete ===\n');
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Connection failed!');
    console.error('\nError details:');
    console.error(`Code: ${error.code}`);
    console.error(`Message: ${error.message}`);

    console.log('\n=== Troubleshooting Tips ===\n');

    if (error.code === '28P01') {
      console.log('❌ Password authentication failed');
      console.log('\nSolutions:');
      console.log('1. Check your .env file has the correct DB_PASSWORD');
      console.log('2. Your PostgreSQL password was set during installation');
      console.log('3. Try opening pgAdmin - the password you use there is the one you need');
      console.log('4. To reset password, run as admin:');
      console.log('   psql -U postgres');
      console.log('   ALTER USER postgres WITH PASSWORD \'new_password\';');
    } else if (error.code === 'ECONNREFUSED') {
      console.log('❌ PostgreSQL server is not running');
      console.log('\nSolutions:');
      console.log('1. Start PostgreSQL service:');
      console.log('   Windows: services.msc → PostgreSQL → Start');
      console.log('   Mac: brew services start postgresql');
      console.log('   Linux: sudo systemctl start postgresql');
    } else if (error.code === '3D000') {
      console.log('❌ Database does not exist');
      console.log('\nSolution:');
      console.log('1. Open pgAdmin');
      console.log('2. Right-click Databases → Create → Database');
      console.log('3. Name: hotel_restaurant_db');
    } else {
      console.log('Unknown error. Please check PostgreSQL is installed and running.');
    }

    console.log('\n=== End of Test ===\n');
    await pool.end();
    process.exit(1);
  }
}

testConnection();
