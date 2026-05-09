<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Socrapper - Social Media Sentiment Scraper</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <?php if(file_exists(public_path('build/manifest.json'))): ?>
        <?php
            $manifest = json_decode(file_get_contents(public_path('build/manifest.json')), true);
        ?>
        <link rel="stylesheet" href="<?php echo e(asset('build/' . $manifest['resources/js/app.jsx']['css'][0])); ?>">
    <?php endif; ?>
</head>
<body>
    <div id="app"></div>
    
    <?php if(file_exists(public_path('build/manifest.json'))): ?>
        <?php
            $manifest = json_decode(file_get_contents(public_path('build/manifest.json')), true);
        ?>
        <script type="module" src="<?php echo e(asset('build/' . $manifest['resources/js/app.jsx']['file'])); ?>"></script>
    <?php endif; ?>
</body>
</html>
<?php /**PATH D:\Advanced\xamp\htdocs\Socrapper\resources\views/app.blade.php ENDPATH**/ ?>