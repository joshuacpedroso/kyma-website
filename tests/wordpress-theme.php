<?php
/** Integration checks for an explicitly isolated WordPress test fixture.
 * KYMA_WP_TEST_ROOT points to the WordPress directory; KYMA_WP_TEST_FIXTURE to
 * JSON IDs named home/about/news/contact. wp-config must define
 * KYMA_THEME_TEST_ENV=true. Never run this against a production installation.
 */
if(PHP_SAPI!=='cli')exit(2);
$root=getenv('KYMA_WP_TEST_ROOT');$fixture=getenv('KYMA_WP_TEST_FIXTURE');
if(!$root||!$fixture)exit("Set KYMA_WP_TEST_ROOT and KYMA_WP_TEST_FIXTURE for an isolated fixture.\n");
require rtrim($root,'/').'/wp-load.php';
if(!defined('KYMA_THEME_TEST_ENV')||KYMA_THEME_TEST_ENV!==true)exit("Refusing to modify a non-test installation.\n");
$f=json_decode(file_get_contents($fixture),true);
$admins=get_users(['role'=>'administrator','number'=>1]);wp_set_current_user($admins[0]->ID);
function kyma_test_assert($condition,$message){if(!$condition)throw new RuntimeException($message);echo 'PASS '.$message.PHP_EOL;}
$ids=kyma_page_ids();
kyma_test_assert(count($ids)===15,'15 managed pages');
kyma_test_assert((int)get_option('page_on_front')===$ids['inicio'],'automatic homepage');
kyma_test_assert($ids['quem-somos']===$f['about'],'matching legacy slug reused');
kyma_test_assert(get_post_status($f['home'])==='draft'&&get_post_status($f['news'])==='draft','legacy content retained as drafts');
kyma_test_assert(get_option('kyma_previous_site')['posts'][$f['about']]['meta']['_elementor_data'][0]==='OLD BUILDER DATA','legacy metadata backed up');
$before=[wp_count_posts('page')->publish,wp_count_posts('post')->publish];kyma_activate();
kyma_test_assert($before===[wp_count_posts('page')->publish,wp_count_posts('post')->publish],'repeat activation does not duplicate');
$id=$ids['haus'];$original=get_post_meta($id,'_kyma_progress',true);
$_POST=['kyma_progress'=>'84.5','kyma_stage_name'=>['Estrutura','Acabamentos'],'kyma_stage_percent'=>['100','69']];
do_action('save_post_page',$id);kyma_test_assert(get_post_meta($id,'_kyma_progress',true)===$original,'nonce required');
$_POST['kyma_progress_nonce']=wp_create_nonce('kyma_save_progress');do_action('save_post_page',$id);
$data=get_post_meta($id,'_kyma_progress',true);kyma_test_assert($data['progress_percent']===84.5&&!$data['progress_is_demo']&&count($data['progress_stages'])===2,'native progress save');
update_post_meta($id,'_kyma_progress',$original);$_POST=[];
$post=wp_insert_post(['post_type'=>'post','post_status'=>'publish','post_title'=>'Notícia de integração Kyma','post_content'=>'Teste nativo.']);
kyma_test_assert(str_contains(kyma_news_highlights(),'Notícia de integração Kyma'),'native post appears on homepage');wp_delete_post($post,true);
if(in_array('--restore',$argv,true)){
 $backup=get_option('kyma_previous_site');kyma_restore_snapshot($backup,true);
 kyma_test_assert(get_stylesheet()==='legacy'&&get_post_status($f['home'])==='publish'&&get_post_status($f['news'])==='publish','legacy theme and posts restored');
 kyma_test_assert(get_post_field('post_content',$f['about'])==='Texto institucional antigo'&&get_post_meta($f['about'],'_elementor_data',true)==='OLD BUILDER DATA','original body and metadata restored');
 foreach($backup['created_ids'] as $created)kyma_test_assert(get_post_status($created)==='draft','new content preserved as draft');
}
