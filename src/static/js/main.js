// JavaScript principal otimizado para performance
document.addEventListener('DOMContentLoaded', function() {
  // Inicialização de tooltips do Bootstrap
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Inicialização de popovers do Bootstrap
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Função para filtrar tabelas
  const searchInputs = document.querySelectorAll('.table-search');
  searchInputs.forEach(input => {
    input.addEventListener('keyup', function() {
      const searchValue = this.value.toLowerCase();
      const tableId = this.getAttribute('data-table-target');
      const table = document.getElementById(tableId);
      
      if (!table) return;
      
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchValue) ? '' : 'none';
      });
    });
  });

  // Função para confirmar exclusões
  const confirmButtons = document.querySelectorAll('.confirm-action');
  confirmButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      const message = this.getAttribute('data-confirm-message') || 'Tem certeza que deseja realizar esta ação?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // Função para paginação no cliente
  const paginationContainers = document.querySelectorAll('.pagination-container');
  paginationContainers.forEach(container => {
    const tableId = container.getAttribute('data-table');
    const table = document.getElementById(tableId);
    const itemsPerPage = parseInt(container.getAttribute('data-items-per-page')) || 10;
    
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const pageCount = Math.ceil(rows.length / itemsPerPage);
    
    if (pageCount <= 1) {
      container.style.display = 'none';
      return;
    }
    
    // Criar paginação
    const paginationList = document.createElement('ul');
    paginationList.className = 'pagination';
    
    for (let i = 1; i <= pageCount; i++) {
      const pageItem = document.createElement('li');
      pageItem.className = 'page-item' + (i === 1 ? ' active' : '');
      
      const pageLink = document.createElement('a');
      pageLink.className = 'page-link';
      pageLink.href = '#';
      pageLink.textContent = i;
      pageLink.addEventListener('click', function(e) {
        e.preventDefault();
        showPage(i);
      });
      
      pageItem.appendChild(pageLink);
      paginationList.appendChild(pageItem);
    }
    
    container.appendChild(paginationList);
    
    // Função para mostrar página específica
    function showPage(page) {
      const start = (page - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      
      rows.forEach((row, index) => {
        row.style.display = (index >= start && index < end) ? '' : 'none';
      });
      
      // Atualizar classe ativa
      const pageItems = container.querySelectorAll('.page-item');
      pageItems.forEach((item, index) => {
        item.className = 'page-item' + (index + 1 === page ? ' active' : '');
      });
    }
    
    // Mostrar primeira página inicialmente
    showPage(1);
  });
});
