from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'stock', 'categories']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and hasattr(self.user, 'business'):
            self.fields['categories'].queryset = Category.objects.filter(
                business=self.user.business
            )
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


    #def __init__(self, *args, **kwargs):
     #   self.business = kwargs.pop('business', None)
      #  super().__init__(*args, **kwargs)
       # if self.business:
        #    self.fields['category'].queryset = Category.objects.filter(business=self.business)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['name'].widget.attrs.update({
            'placeholder': 'e.g. Electronics, Clothing'
        })
    