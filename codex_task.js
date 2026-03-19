// codex_task.js - Task Runner for GitHub Remote Connector

const { exec } = require('child_process');
const args = process.argv.slice(2);

// Function to execute a command
function execute(command) {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(`Error: ${stderr}`);
            }
            resolve(stdout);
        });
    });
}

// Function to run GitHub connector tasks
async function runTask(task) {
    try {
        const output = await execute(task);
        console.log(`Task Output: ${output}`);
    } catch (error) {
        console.error(error);
    }
}

if (args.length === 0) {
    console.error('Usage: node codex_task.js "<command>"');
    process.exit(1);
}

const task = args.join(' ');
runTask(task);
