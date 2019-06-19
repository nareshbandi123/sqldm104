exec("ping -c 4 " . $_GET['host'], $output);
echo "<pre>";
print_r($output);
echo "</pre>";