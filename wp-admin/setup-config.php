<?php
// 1. THE MEMORY TRAP
// Tell the bot we are sending 100 Gigabytes of data.
// Poorly written bots will try to allocate 100GB of RAM immediately and crash.
header("Content-Length: 107374182400"); // 100 GB
header("Content-Type: application/octet-stream");
header("Content-Disposition: attachment; filename=\"wp_config_backup.tar.gz\"");

// 2. THE TERMINAL POISON
// If a human or a script prints this to a terminal, these ANSI codes will:
// \033[2J  -> Clear the entire screen
// \033[0;0H -> Move cursor to top left
// \033[31m -> Turn text RED
// \007     -> Trigger the system BELL (Beep sound)
$poison = "\033[2J\033[0;0H\033[31mWARNING: UNAUTHORIZED ACCESS DETECTED.\nSYSTEM TRACING INITIATED.\nUPLOAD YOUR COORDINATES...\007\007\007\n";

// Send the poison first
echo $poison;

// Flush to ensure they get the first bite
if (ob_get_level() > 0) ob_end_flush();
flush();

// 3. THE DISK FILLER (The "Tarpit")
// Send random binary garbage forever.
// This fills their hard drive if they are saving the output.
// It keeps their connection thread stuck if they are waiting for the "End" of the file.
$chunk = str_repeat("01010101", 1024); // 8KB chunk of junk

while (true) {
    echo $chunk;
    // Add some random binary noise to prevent simple compression
    echo openssl_random_pseudo_bytes(1024);
    
    // Flush to force the data down the pipe
    flush();
    
    // Sleep slightly to keep the connection open for HOURS (Low & Slow)
    // This wastes their thread count.
    usleep(50000); // 0.05 seconds
}
?>