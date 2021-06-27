<script>
	export let api;
	let choose_mode = 0;
	let categoriesP;
	let cat_selected;
	$: categoriesP = api ? api.getCategories() : null;
</script>

<section>
<aside>
	<h1>Add content</h1>
	Category :
	{#if choose_mode == 1}
		{#await categoriesP}
		{:then categories}
			<select bind:value={cat_selected}>
		{#each categories as cat}
			<option value={cat}>
				{cat}
			</option>
		{/each}
			</select>
		{/await}
	{/if}
	{#if choose_mode == 2}
		<input type="text" bind:value={cat_selected}  placeholder="Name" />
	{/if}
	{#if choose_mode == 0}<a on:click={()=>choose_mode=1} href="#">Choose existant category</a> / <a on:click={()=>{choose_mode=2; cat_selected=''}} href="#">Add a new one</a>
	{:else}
	<a on:click={()=>choose_mode=0} href="#">Cancel</a>
	<button>Add</button>
	{/if}
</aside>
</section>