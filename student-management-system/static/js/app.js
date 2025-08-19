// 学生信息管理系统 - 前端JavaScript

$(document).ready(function() {
    // 初始化提示框
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // 自动隐藏警告提示
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // 确认删除对话框
    $('.delete-btn').click(function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        const itemName = $(this).data('name') || '该项目';
        
        if (confirm(`确定要删除 ${itemName} 吗？此操作无法撤销。`)) {
            window.location.href = url;
        }
    });
    
    // 搜索表单自动提交
    $('.search-input').on('input', debounce(function() {
        $(this).closest('form').submit();
    }, 500));
    
    // 状态筛选自动提交
    $('.status-filter, .category-filter').change(function() {
        $(this).closest('form').submit();
    });
});

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API工具函数
const API = {
    // 基础请求函数
    request: function(method, url, data = null) {
        return $.ajax({
            url: url,
            method: method,
            data: data ? JSON.stringify(data) : null,
            contentType: 'application/json',
            dataType: 'json'
        });
    },
    
    // GET请求
    get: function(url) {
        return this.request('GET', url);
    },
    
    // POST请求
    post: function(url, data) {
        return this.request('POST', url, data);
    },
    
    // PUT请求
    put: function(url, data) {
        return this.request('PUT', url, data);
    },
    
    // DELETE请求
    delete: function(url) {
        return this.request('DELETE', url);
    }
};

// 消息提示函数
function showMessage(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : `alert-${type}`;
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 移除现有警告
    $('.alert').remove();
    
    // 添加新警告
    $('main .container-fluid').prepend(alertHtml);
    
    // 自动隐藏
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
}

// 加载动画控制
function showLoading(container = 'body') {
    $(container).append('<div class="loading"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div></div>');
    $('.loading').show();
}

function hideLoading() {
    $('.loading').remove();
}

// 表单验证
function validateForm(formSelector) {
    const form = $(formSelector);
    let isValid = true;
    
    // 清除之前的验证状态
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').remove();
    
    // 验证必填字段
    form.find('[required]').each(function() {
        const field = $(this);
        if (!field.val().trim()) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">此字段为必填项</div>');
            isValid = false;
        }
    });
    
    // 验证邮箱格式
    form.find('input[type="email"]').each(function() {
        const field = $(this);
        const email = field.val().trim();
        if (email && !isValidEmail(email)) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">邮箱格式不正确</div>');
            isValid = false;
        }
    });
    
    // 验证手机号格式
    form.find('input[name="phone"]').each(function() {
        const field = $(this);
        const phone = field.val().trim();
        if (phone && !isValidPhone(phone)) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">手机号格式不正确</div>');
            isValid = false;
        }
    });
    
    return isValid;
}

// 邮箱验证
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 手机号验证
function isValidPhone(phone) {
    const phoneRegex = /^1[3-9]\d{9}$/;
    return phoneRegex.test(phone);
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// 格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 状态显示
function getStatusBadge(status, type = 'student') {
    const statusMap = {
        student: {
            'active': '<span class="badge bg-success">在读</span>',
            'graduated': '<span class="badge bg-info">已毕业</span>',
            'suspended': '<span class="badge bg-warning">休学</span>'
        },
        course: {
            'active': '<span class="badge bg-success">开放选课</span>',
            'closed': '<span class="badge bg-warning">关闭选课</span>',
            'finished': '<span class="badge bg-secondary">已结束</span>'
        },
        book: {
            'available': '<span class="badge bg-success">可借阅</span>',
            'unavailable': '<span class="badge bg-danger">不可借阅</span>'
        },
        borrow: {
            'borrowed': '<span class="badge bg-warning">已借出</span>',
            'returned': '<span class="badge bg-success">已归还</span>',
            'overdue': '<span class="badge bg-danger">逾期</span>',
            'lost': '<span class="badge bg-dark">丢失</span>'
        }
    };
    
    return statusMap[type] && statusMap[type][status] 
        ? statusMap[type][status] 
        : `<span class="badge bg-secondary">${status}</span>`;
}
